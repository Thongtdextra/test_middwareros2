ROS 2 Middleware Benchmark: FastDDS vs Zenoh trên Mạng Không Ổn Định
Dự án này cung cấp bộ công cụ và quy trình để đánh giá hiệu năng (Throughput, Latency, Resilience) của hai cấu hình middleware ROS 2 Humble phổ biến: rmw_fastrtps_cpp (với DDS Router) và rmw_zenoh_cpp (với Zenoh Router). Mục tiêu là xác định giải pháp tối ưu cho Mobile Robots (Rover) hoạt động trong môi trường WiFi/WAN suy hao.

1. Yêu cầu Hệ thống (Prerequisites)
OS: Ubuntu 22.04 LTS

ROS 2: Humble Hawksbill

Docker: Phiên bản 20.10+

Phần cứng: 2 máy tính (hoặc 1 máy mạnh chạy 2 container tách biệt mạng)

Network Tools: iproute2 (cho lệnh tc), python3

2. Cài đặt và Build
Clone repository và build các Docker image:bash git clone -b middlewareros_amd64 https://gitlab.phenikaax.com/sonlv/rover.git cd rover

Build image cho Fast DDS
cd /home/<User>/test_middwareros2/Dockerbuild/DDS_Router
docker build -t ros2_fastdds_benchmark Dockerfile

Build image cho Zenoh
cd /home/<User>/test_middwareros2/Dockerbuild/Zenoh
docker build -t ros2_zenoh_benchmark Dockerfile

3. Quy Trình Kiểm Tra Chi Tiết

Quy trình kiểm tra được thiết kế để mô phỏng các kịch bản thực tế trong hệ thống phân tán, tập trung vào publisher-subscriber (pub-sub) với quy mô khác nhau. Các kiểm tra được thực hiện trên hai middleware: Fast DDS + DDS Router và Zenoh + Zenoh Router.

3.1. Tại device (mobile): Bắt WiFi hotspot và gửi topic

ros2 topic pub /b2/testreliable1hz std_msgs/msg/String "{data: 'Hello, ROS 2'}" --rate 5 --qos-reliability best_effort

 Mô Phỏng Gián Đoạn Mạng: Sử dụng công cụ tc (Traffic Control) để áp dụng các điều kiện mạng kém:
 #Xóa cấu hình cũ:
sudo tc qdisc del dev eno1 root
 
#Thêm trễ 100ms và mất 10% gói:
sudo tc qdisc add dev eno1 root netem delay 100ms loss 10%
 
#Thêm trễ 200ms và mất 20% gói:
sudo tc qdisc add dev eno1 root netem delay 200ms loss 20%
 

3.2. Tại server: Chạy script giám sát realtime

./monitor_hz_ping.py /b2/testreliable1hz [IP_gateway]

Script đo Hz, ping, phát hiện NO_MESSAGE, và log CSV chi tiết.


