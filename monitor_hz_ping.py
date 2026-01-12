#!/usr/bin/env python3

import subprocess
import threading
import time
import re
import datetime
import queue
import os
import sys

# === Xử lý arguments từ command line ===
# ./monitor_hz_ping.py <Topic_name> [IP]
if len(sys.argv) >= 2:
    TOPIC = sys.argv[1].strip()
else:
    TOPIC = "/test_middleware_hz"  # Default topic

if len(sys.argv) >= 3:
    PING_IP = sys.argv[2].strip()
else:
    PING_IP = "8.8.8.8"  # Default IP

# === Lấy RMW_IMPLEMENTATION ===
RMW = os.getenv('RMW_IMPLEMENTATION', 'unknown')
RMW_SHORT = RMW.replace('rmw_', '').replace('_impl', '').replace('_cpp', '')

# === Tạo tên file log sạch và duy nhất ===
# Thay thế ký tự không hợp lệ trong topic name
topic_clean = TOPIC.strip('/').replace('/', '_')
ip_clean = PING_IP.replace('.', '-')
start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

LOG_FILE = f"hz_ping_log_{RMW_SHORT}_{topic_clean}_{ip_clean}_{start_time}.csv"

# Queues
hz_queue = queue.Queue()
ping_queue = queue.Queue()

# Regex
hz_regex = re.compile(r"average rate:\s*([\d\.]+)")
ping_regex = re.compile(r"time=([\d\.]+) ms")

# Thời gian nhận message cuối cùng
last_message_time = time.time()

def run_ros2_hz():
    global last_message_time
    cmd = ["ros2", "topic", "hz", TOPIC]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in proc.stdout:
        line = line.strip()
        if "average rate" in line:
            match = hz_regex.search(line)
            if match:
                hz = float(match.group(1))
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                hz_queue.put((timestamp, hz))
                last_message_time = time.time()
        print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]} | HZ: {line}")

def run_ping():
    cmd = ["ping", PING_IP]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1)
    for line in proc.stdout:
        line = line.strip()
        if "time=" in line and "bytes from" in line:
            match = ping_regex.search(line)
            if match:
                ping_ms = float(match.group(1))
                # Timestamp Asia/Ho_Chi_Minh (UTC+7)
                timestamp = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                ping_queue.put((timestamp, ping_ms))
        ts = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"{ts} | PING: {line}")

def logger():
    global last_message_time

    with open(LOG_FILE, "w") as f:
        f.write("timestamp,hz,ping_time_ms,status\n")

        last_hz = None
        last_hz_time = None
        last_ping = None

        while True:
            while not hz_queue.empty():
                last_hz_time, last_hz = hz_queue.get()

            while not ping_queue.empty():
                ping_time, ping_ms = ping_queue.get()
                last_ping = (ping_time, ping_ms)

            # Phát hiện mất message > 3 giây
            if time.time() - last_message_time > 3.0:
                status = "NO_MESSAGE"
                ping_str = last_ping[1] if last_ping else "N/A"
                log_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                f.write(f"{log_time},0.000,{ping_str},{status}\n")
                f.flush()
                print(f"[{log_time}] NO_MESSAGE detected")

            # Ghi log khi có Hz mới
            if last_hz is not None and last_hz_time:
                status = "NORMAL" if last_hz >= 4.5 else "LOW_HZ"
                ping_str = last_ping[1] if last_ping else "N/A"
                f.write(f"{last_hz_time},{last_hz:.3f},{ping_str},{status}\n")
                f.flush()
                print(f"[{last_hz_time}] Hz: {last_hz:.3f} | Ping: {ping_str} ms | {status}")

                last_hz = None

            time.sleep(0.5)

if __name__ == "__main__":
    print("=== ROS2 Hz + Ping Monitor ===")
    print(f"Topic giám sát   : {TOPIC}")
    print(f"IP ping          : {PING_IP}")
    print(f"RMW              : {RMW}")
    print(f"File log         : {LOG_FILE}")
    print("===============================")

    threading.Thread(target=run_ros2_hz, daemon=True).start()
    threading.Thread(target=run_ping, daemon=True).start()
    threading.Thread(target=logger, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDừng giám sát. Log đã lưu tại:", LOG_FILE)
