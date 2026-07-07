# Loomo Bridge

Python-based control interface for Segway Loomo robot.

## Connection Methods

### 1. ADB over WiFi (Development Mode)
Most common for development. Loomo runs Android and exposes ADB over WiFi.

### 2. ROS Bridge
External computer (like a Jetson) runs ROS and bridges to Loomo's native interface.

### 3. Bluetooth
For mobile app control via the Loomo SDK.

## Setup

### Prerequisites
- Loomo robot powered on and connected to WiFi
- ADB installed on your computer
- Loomo's IP address

### Connect via ADB
```bash
adb connect <LOOMO_IP>:5555
adb devices  # Should show Loomo device
```

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

## Usage

```python
from loomo_bridge import LoomoClient

# Connect to Loomo
loomo = LoomoClient(host="192.168.42.129")

# Basic movement
loomo.move_forward(speed=0.5, duration=2.0)
loomo.turn_left(angle=90)
loomo.stop()

# Access sensors
print(loomo.get_battery_level())
print(loomo.get_pose())
```

## API Reference

See `loomo_bridge/loomo_client.py` for full API documentation.
