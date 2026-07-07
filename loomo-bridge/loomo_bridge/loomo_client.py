"""
LoomoClient - Main interface for controlling Segway Loomo robot.

Supports multiple connection backends:
- ADB: Direct Android Debug Bridge connection
- ROS: ROS bridge via external node
- WebSocket: Direct socket connection to Loomo app
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LoomoPose:
    """Robot pose data."""
    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class SensorData:
    """Sensor readings from Loomo."""
    battery_percent: int
    battery_voltage: float
    is_charging: bool
    ultrasonic_distance: float  # cm
    cliff_detected: bool
    obstacle_detected: bool


class LoomoClient:
    """
    Main client for controlling Segway Loomo robot.
    
    Usage:
        loomo = LoomoClient(host="192.168.42.129", connection_type="adb")
        await loomo.connect()
        await loomo.move_forward(speed=0.5, duration=2.0)
        await loomo.disconnect()
    """
    
    def __init__(self, host: str = "192.168.42.129", 
                 port: int = 5555,
                 connection_type: str = "adb",
                 ros_master_uri: Optional[str] = None):
        """
        Initialize Loomo client.
        
        Args:
            host: IP address of Loomo
            port: Port for connection (default 5555 for ADB)
            connection_type: "adb", "ros", or "websocket"
            ros_master_uri: ROS master URI (if using ROS connection)
        """
        self.host = host
        self.port = port
        self.connection_type = connection_type
        self.ros_master_uri = ros_master_uri
        
        self._connected = False
        self._bridge = None
        self._sensor_callbacks: list[Callable] = []
        
        logger.info(f"LoomoClient initialized ({connection_type} mode): {host}:{port}")
    
    async def connect(self) -> bool:
        """Establish connection to Loomo."""
        try:
            if self.connection_type == "adb":
                from .adb_bridge import ADBBridge
                self._bridge = ADBBridge(self.host, self.port)
            elif self.connection_type == "ros":
                from .ros_bridge import ROSBridge
                self._bridge = ROSBridge(self.host, self.ros_master_uri)
            elif self.connection_type == "websocket":
                from .websocket_bridge import WebSocketBridge
                self._bridge = WebSocketBridge(self.host, self.port)
            else:
                raise ValueError(f"Unknown connection type: {self.connection_type}")
            
            self._connected = await self._bridge.connect()
            return self._connected
            
        except Exception as e:
            logger.error(f"Failed to connect to Loomo: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Loomo."""
        if self._bridge:
            await self._bridge.disconnect()
            self._connected = False
    
    # Movement Commands
    async def move(self, linear_velocity: float = 0.0, 
                   angular_velocity: float = 0.0,
                   duration: Optional[float] = None) -> bool:
        """
        Move Loomo with specified velocities.
        
        Args:
            linear_velocity: Forward/backward speed (m/s), positive = forward
            angular_velocity: Rotation speed (rad/s), positive = counter-clockwise
            duration: Time to maintain velocity (seconds), None = indefinite
        """
        if not self._connected:
            logger.error("Not connected to Loomo")
            return False
        
        return await self._bridge.send_velocity_command(
            linear_velocity, angular_velocity, duration
        )
    
    async def move_forward(self, speed: float = 0.5, duration: float = 1.0) -> bool:
        """Move forward at specified speed for duration."""
        return await self.move(linear_velocity=speed, duration=duration)
    
    async def move_backward(self, speed: float = 0.5, duration: float = 1.0) -> bool:
        """Move backward at specified speed for duration."""
        return await self.move(linear_velocity=-speed, duration=duration)
    
    async def turn_left(self, angular_speed: float = 0.5, duration: float = 1.0) -> bool:
        """Turn left at specified angular speed."""
        return await self.move(angular_velocity=angular_speed, duration=duration)
    
    async def turn_right(self, angular_speed: float = 0.5, duration: float = 1.0) -> bool:
        """Turn right at specified angular speed."""
        return await self.move(angular_velocity=-angular_speed, duration=duration)
    
    async def stop(self) -> bool:
        """Stop all movement."""
        return await self.move(linear_velocity=0.0, angular_velocity=0.0)
    
    # Head/Camera Control
    async def set_head_pose(self, yaw: float = 0.0, pitch: float = 0.0) -> bool:
        """
        Set head position (camera orientation).
        
        Args:
            yaw: Horizontal angle in degrees (-90 to 90)
            pitch: Vertical angle in degrees (-30 to 30)
        """
        if not self._connected:
            return False
        return await self._bridge.send_head_command(yaw, pitch)
    
    async def reset_head(self) -> bool:
        """Reset head to center position."""
        return await self.set_head_pose(0.0, 0.0)
    
    # Sensor Data
    async def get_battery_level(self) -> Optional[int]:
        """Get battery percentage (0-100)."""
        if not self._connected:
            return None
        return await self._bridge.get_battery_level()
    
    async def get_pose(self) -> Optional[LoomoPose]:
        """Get current robot pose."""
        if not self._connected:
            return None
        return await self._bridge.get_pose()
    
    async def get_sensor_data(self) -> Optional[SensorData]:
        """Get complete sensor data."""
        if not self._connected:
            return None
        return await self._bridge.get_sensor_data()
    
    async def get_ultrasonic_distance(self) -> Optional[float]:
        """Get ultrasonic sensor distance in cm."""
        if not self._connected:
            return None
        return await self._bridge.get_ultrasonic_distance()
    
    # Camera
    async def get_camera_frame(self) -> Optional[bytes]:
        """Get current camera frame as JPEG bytes."""
        if not self._connected:
            return None
        return await self._bridge.get_camera_frame()
    
    async def start_camera_stream(self, callback: Callable):
        """Start continuous camera stream with callback."""
        if not self._connected:
            return False
        return await self._bridge.start_camera_stream(callback)
    
    async def stop_camera_stream(self):
        """Stop camera stream."""
        if self._connected and self._bridge:
            await self._bridge.stop_camera_stream()
    
    # Audio
    async def speak(self, text: str) -> bool:
        """Make Loomo speak text."""
        if not self._connected:
            return False
        return await self._bridge.speak(text)
    
    async def play_sound(self, sound_file: str) -> bool:
        """Play sound file on Loomo."""
        if not self._connected:
            return False
        return await self._bridge.play_sound(sound_file)
    
    # Status
    @property
    def is_connected(self) -> bool:
        """Check if connected to Loomo."""
        return self._connected
    
    async def ping(self) -> bool:
        """Check if Loomo is responsive."""
        if not self._connected:
            return False
        return await self._bridge.ping()
