FROM ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive

# Cài đặt đầy đủ các tools cần thiết cho build từ source
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    ca-certificates \
    python3-vcstool \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    ros-humble-demo-nodes-cpp \
    libyaml-cpp-dev \
    libasio-dev \
    libtinyxml2-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Cài đặt Python dependencies
RUN pip3 install --no-cache-dir \
    kconfiglib \
    jinja2 \
    pyserial \
    empy \
    packaging \
    toml \
    numpy \
    pyyaml \
    pyros-genmsg \
    jsonschema

# ------ Build DDS Router từ source ------
WORKDIR /DDS-Router-3.2

# Tải .repos và import các repository phụ thuộc
RUN mkdir -p src \
    && wget https://raw.githubusercontent.com/eProsima/DDS-Router/main/ddsrouter.repos \
    && vcs import src < ddsrouter.repos

# Cài đặt system dependencies qua rosdep (rất quan trọng)
RUN rosdep init || echo "rosdep already initialized" \
    && rosdep update \
    && rosdep install --from-paths src --ignore-src -r -y

# Build workspace
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"

# Copy file config template của bạn
COPY dds_config_template.yaml /DDS-Router-3.2/dds_config_template.yaml

# Dọn dẹp source code để giảm kích thước image (~500-600MB tiết kiệm)
#RUN rm -rf src

# ------ Environment variables ------
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
    ROS_DOMAIN_ID=2 \
    ROS_LOCALHOST_ONLY=1

# Tự động source khi mở terminal
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc \
    && echo "source /DDS-Router-3.2/install/setup.bash" >> /root/.bashrc

WORKDIR /root
CMD ["bash"]