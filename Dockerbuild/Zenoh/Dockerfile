FROM ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive

# Cài tools cơ bản và các package ROS cần thiết
RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    git \
    ros-humble-demo-nodes-cpp \
    ros-humble-rmw-zenoh-cpp \
    geographiclib-tools 

# Cài geoid model EG96-5 (dùng cho chuyển đổi độ cao nếu cần)
RUN geographiclib-get-geoids egm96-5
# Set environment variables toàn cục (đảm bảo luôn có, kể cả non-interactive shell)
ENV RMW_IMPLEMENTATION=rmw_zenoh_cpp \
    ZENOH_ROUTER_CONFIG_URI=/workspaces/Zenoh/routerconfig.json5 \
    ROS_DOMAIN_ID=0 \
    ROS_LOCALHOST_ONLY=1
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc
CMD ["bash"]