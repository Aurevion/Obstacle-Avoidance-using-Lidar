# Obstacle Avoidance using LiDAR

A distributed obstacle detection system using RPLIDAR C1 on Raspberry Pi 5 with ROS 2 Jazzy. Real-time LiDAR scan data is streamed from the robot to a remote laptop via secure networking (Tailscale) for intelligent obstacle detection and avoidance.

## Features

- **Real-time LiDAR Scanning**: RPLIDAR C1 continuous 2D scanning capability
- **Distributed Architecture**: Sensor data collection on embedded device, processing on remote machine
- **ROS 2 Integration**: Uses ROS 2 Jazzy for middleware and pub/sub communication
- **Secure Remote Communication**: Data streaming via rmw_zenoh over Tailscale VPN
- **Obstacle Detection**: Intelligent detection of obstacles from LiDAR scan distances
- **Low Latency**: Optimized for near real-time processing

## Hardware Requirements

- **Raspberry Pi 5** (or compatible ARM64 Linux device)
- **RPLIDAR C1** LiDAR sensor
  - 2D scanning capability
  - 25m scanning range
  - USB interface
- **USB Connection** between Raspberry Pi and LiDAR
- **Network Interface** for Tailscale connectivity (WiFi or Ethernet)
- **Laptop/Desktop** for remote processing (Linux, macOS, or Windows with WSL)

## Software Requirements

### Raspberry Pi 5
- **OS**: Ubuntu 24.04 or Raspberry Pi OS (64-bit)
- **ROS 2 Jazzy** or later
- **Python 3.10+**
- **rmw_zenoh** (ROS middleware)
- **Tailscale** VPN client

### Laptop/Remote Machine
- **OS**: Ubuntu 24.04
- **ROS 2 Jazzy** (already installed)
- **Python 3.10+**
- **Tailscale** VPN client

## Installation

### 1. Raspberry Pi 5 Setup

#### Install ROS 2 Jazzy

Follow the official installation guide: [ROS 2 Jazzy Installation](https://docs.ros.org/en/jazzy/Installation.html)

For Raspberry Pi, ensure you install the ARM64 version.

#### Install rmw_zenoh
```bash
sudo apt install ros-jazzy-rmw-zenoh-cpp
```

#### Install RPLIDAR ROS Package
```bash
cd ~/ros2_ws/src
git clone -b ros2 https://github.com/Slamtec/rplidar_ros.git
```

#### Install Tailscale
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

#### Clone and Setup Project
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/Aurevion/Obstacle-Avoidance-using-Lidar.git
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
```

### 2. Laptop/Remote Machine Setup

#### Install ROS 2 Jazzy

Follow the official installation guide: [ROS 2 Jazzy Installation](https://docs.ros.org/en/jazzy/Installation.html)

#### Install rmw_zenoh
```bash
sudo apt install ros-jazzy-rmw-zenoh-cpp
```

#### Install Tailscale
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

#### Clone and Setup Project
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/Aurevion/Obstacle-Avoidance-using-Lidar.git
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
```

## Configuration

### Network Configuration (Tailscale)

1. **Raspberry Pi**:
   ```bash
   sudo tailscale up
   # Note the assigned IP address
   ```

2. **Laptop**:
   ```bash
   sudo tailscale up
   ```

3. **Verify Connectivity**:
   ```bash
   ping <raspberry-pi-tailscale-ip>
   ```

### ROS 2 Environment

Set middleware to Zenoh on both machines:
```bash
export RMW_IMPLEMENTATION=rmw_zenoh_cpp
```

#### Zenoh TCP Connection Configuration (Laptop Only)

Configure Zenoh to connect to the Raspberry Pi via TCP over Tailscale. Replace `100.x.y.z` with the Raspberry Pi's Tailscale IP:

```bash
export ZENOH_CONFIG_OVERRIDE='mode="client";connect/endpoints=["tcp/100.x.y.z:7447"]'
```

Add to ~/.bashrc for persistence:
```bash
echo 'export RMW_IMPLEMENTATION=rmw_zenoh_cpp' >> ~/.bashrc
echo 'export ZENOH_CONFIG_OVERRIDE='"'"'mode="client";connect/endpoints=["tcp/100.x.y.z:7447"]'"'"'' >> ~/.bashrc
source ~/.bashrc
```

**Note**: Replace `100.x.y.z` with your Raspberry Pi's actual Tailscale IP address (find it using `tailscale ip -4` on the Pi).

Add to ~/.bashrc for persistence on Raspberry Pi:
```bash
echo "export RMW_IMPLEMENTATION=rmw_zenoh_cpp" >> ~/.bashrc
source ~/.bashrc
```

### RPLIDAR Configuration

Connect the RPLIDAR C1 via USB to the Raspberry Pi. The LiDAR node will automatically detect and initialize the sensor.

Verify connectivity:
```bash
ls -la /dev/ttyUSB*
```

## Usage

### On Raspberry Pi (Sensor Node)

1. **Source ROS 2**:
   ```bash
   source /opt/ros/jazzy/setup.bash
   source ~/ros2_ws/install/setup.bash
   ```

2. **Launch LiDAR Publisher**:
   ```bash
   ros2 launch rplidar_ros rplidar_c1_launch.py
   ```

This will start publishing `/scan` messages from the RPLIDAR C1.

### On Laptop (Processing Node)

1. **Source ROS 2**:
   ```bash
   source /opt/ros/jazzy/setup.bash
   source ~/ros2_ws/install/setup.bash
   ```

2. **Run Safety Node**:
   ```bash
   ros2 run lidar_safety safety_node
   ```

This will subscribe to the LiDAR `/scan` topic and perform obstacle detection.

### Monitor Data

View published topics:
```bash
ros2 topic list
ros2 topic echo /cmd_vel
```

## System Architecture

```
┌─────────────────────────────────────────┐
│         Raspberry Pi 5                   │
│  ┌────────────────────────────────────┐ │
│  │  RPLIDAR C1 (USB Connected)        │ │
│  └────────────────────────────────────┘ │
│                   ▼                      │
│  ┌────────────────────────────────────┐ │
│  │  ROS 2 LiDAR Publisher Node        │ │
│  │  - Reads scan data                 │ │
│  │  - Publishes /scan topic           │ │
│  └────────────────────────────────────┘ │
│                   ▼                      │
│  ┌────────────────────────────────────┐ │
│  │  rmw_zenoh Middleware              │ │
│  │  (Tailscale VPN Transport)         │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
         ▼ (Network Traffic)
┌─────────────────────────────────────────┐
│         Laptop/Desktop                   │
│  ┌────────────────────────────────────┐ │
│  │  rmw_zenoh Middleware              │ │
│  │  (Tailscale VPN Transport)         │ │
│  └────────────────────────────────────┘ │
│                   ▼                      │
│  ┌────────────────────────────────────┐ │
│  │  ROS 2 Obstacle Detector Node      │ │
│  │  - Subscribes to /scan topic       │ │
│  │  - Processes scan distances        │ │
│  │  - Publishes /obstacle_detection   │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Project Structure

```
Obstacle-Avoidance-using-Lidar/
├── README.md
├── lidar_safety/
│   ├── setup.py
│   ├── setup.cfg
│   ├── package.xml
│   └── lidar_safety/
│       ├── __init__.py
│       └── safety_node.py
└── ...
```

## Troubleshooting

### LiDAR Not Detected
- Verify USB connection: `lsusb | grep CPRD`
- Check permissions: `sudo usermod -a -G dialout $USER`
- Reboot or re-login for group changes to take effect

### ROS 2 Topics Not Visible
- Verify Tailscale connection: `tailscale status`
- Check middleware setting: `echo $RMW_IMPLEMENTATION`
- Monitor network: `ros2 topic list` on both machines

### Network Timeout Issues
- Verify Tailscale IP: `tailscale ip -4`
- Check firewall: `sudo ufw status`
- Test connectivity: `ping <other-machine-ip>`

### Permission Issues with LiDAR
```bash
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## References

- [RPLIDAR C1 Documentation](https://www.slamtec.com/en/Lidar/C1)
- [ROS 2 Jazzy Documentation](https://docs.ros.org/en/jazzy/)
- [RMW Zenoh](https://github.com/ros2/rmw_zenoh)
- [Tailscale](https://tailscale.com/)

## Author

**Aurevion** - [GitHub Profile](https://github.com/Aurevion)

## Support

For issues, questions, or suggestions, please open an issue on the [GitHub Issues](https://github.com/Aurevion/Obstacle-Avoidance-using-Lidar/issues) page.
