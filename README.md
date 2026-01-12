ROS 2 Middleware Benchmark: FastDDS vs. Zenoh on Unstable Networks
This project provides a toolkit and workflow to evaluate the performance (Throughput, Latency, Resilience) of two common ROS 2 Humble middleware configurations: rmw_fastrtps_cpp (with DDS Router) and rmw_zenoh_cpp (with Zenoh Router). The goal is to determine the optimal solution for Mobile Robots (Rovers) operating in lossy WiFi/WAN environments.

Prerequisites
OS: Ubuntu 22.04 LTS

ROS 2: Humble Hawksbill

Docker: Version 20.10+

Hardware: 2 Computers (or 1 powerful machine running 2 network-isolated containers)

Network Tools: iproute2 (for the tc command), python3

Installation and Build
Clone the repository and build the Docker images:
git clone https://github.com/Thongtdextra/test_middwareros2.git

Build image for Fast DDS:
cd /home/<user>/test_middwareros2/Dockerbuild/DDS_Router
docker build -t ros2_fastdds_benchmark Dockerfile

Build image for Zenoh:
cd /home/<user>/test_middwareros2/Dockerbuild/Zenoh
docker build -t ros2_zenoh_benchmark Dockerfile
Detailed Testing Procedure
The testing process is designed to simulate real-world scenarios in distributed systems, focusing on publisher-subscriber (pub-sub) models at various scales. Tests are performed on two middleware configurations: Fast DDS + DDS Router and Zenoh + Zenoh Router.

On the Device (Mobile): Connect to WiFi Hotspot and Publish Topics
Publish a test topic with specific QoS settings:
ros2 topic pub /b2/testreliable1hz std_msgs/msg/String "{data: 'Hello, ROS 2'}" --rate 5 --qos-reliability best_effort

Network Interruption Simulation: Use the tc (Traffic Control) tool to apply poor network conditions:
# Clear old configuration
sudo tc qdisc del dev eno1 root
# Add 100ms delay and 10% packet loss
sudo tc qdisc add dev eno1 root netem delay 100ms loss 10%
# Add 200ms delay and 20% packet loss
sudo tc qdisc add dev eno1 root netem delay 200ms loss 20%

On the Server: Run Real-time Monitoring Script
Run the python script to monitor the connection and data flow:
./monitor_hz_ping.py /b2/testreliable1hz [IP_gateway]

This script measures Hz, ping latency, detects NO_MESSAGE events, and logs detailed data to a CSV file.
