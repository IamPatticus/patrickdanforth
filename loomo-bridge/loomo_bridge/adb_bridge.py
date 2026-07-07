"""
ADBBridge - Control Loomo via Android Debug Bridge.

This uses ADB to execute commands on the Loomo's Android system.
Requires ADB to be installed and Loomo to have USB debugging enabled.
"""

import asyncio
import subprocess
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ADBBridge:
    """Bridge to Loomo using ADB over WiFi."""
    
    def __init__(self, host: str = "192.168.42.129", port: int = 5555):
        self.host = host
        self.port = port
        self.device_id = f"{host}:{port}"
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to Loomo via ADB."""
        try:
            # Connect to device
            result = await self._run_adb_command(["connect", self.device_id])
            if "connected" in result.lower() or "already connected" in result.lower():
                self._connected = True
                logger.info(f"Connected to Loomo via ADB: {self.device_id}")
                return True
            else:
                logger.error(f"Failed to connect: {result}")
                return False
        except Exception as e:
            logger.error(f"ADB connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Loomo."""
        try:
            await self._run_adb_command(["disconnect", self.device_id])
            self._connected = False
            logger.info("Disconnected from Loomo")
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
    
    async def _run_adb_command(self, args: list) -> str:
        """Run ADB command and return output."""
        cmd = ["adb"] + args
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            raise RuntimeError(f"ADB command failed: {stderr.decode()}")
        
        return stdout.decode().strip()
    
    async def _run_shell_command(self, cmd: str) -> str:
        """Run shell command on Loomo."""
        return await self._run_adb_command(["-s", self.device_id, "shell", cmd])
    
    # Movement Commands
    async def send_velocity_command(self, linear: float, angular: float, 
                                     duration: Optional[float] = None) -> bool:
        """
        Send velocity command to Loomo.
        
        Note: ADB mode requires a companion Android app on Loomo
        that receives these commands. This is a placeholder implementation.
        """
        try:
            # This would need a custom app on Loomo to receive intents
            # Example: am broadcast -a com.loomo.bridge.MOVE --ef linear 0.5 --ef angular 0.0
            cmd = f"am broadcast -a com.loomo.bridge.MOVE " \
                  f"--ef linear {linear} --ef angular {angular}"
            await self._run_shell_command(cmd)
            
            if duration:
                await asyncio.sleep(duration)
                await self.send_velocity_command(0.0, 0.0)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send velocity command: {e}")
            return False
    
    async def send_head_command(self, yaw: float, pitch: float) -> bool:
        """Set head position."""
        try:
            cmd = f"am broadcast -a com.loomo.bridge.HEAD " \
                  f"--ef yaw {yaw} --ef pitch {pitch}"
            await self._run_shell_command(cmd)
            return True
        except Exception as e:
            logger.error(f"Failed to send head command: {e}")
            return False
    
    # Sensor Commands
    async def get_battery_level(self) -> Optional[int]:
        """Get battery level from Android system."""
        try:
            output = await self._run_shell_command(
                "dumpsys battery | grep level | head -1"
            )
            # Parse output like "level: 85"
            level = int(output.split(":")[1].strip())
            return level
        except Exception as e:
            logger.error(f"Failed to get battery: {e}")
            return None
    
    async def get_pose(self) -> Optional[dict]:
        """Get robot pose (requires custom app)."""
        try:
            # Would need custom app to expose this via file or intent
            output = await self._run_shell_command(
                "cat /sdcard/loomo/pose.json 2>/dev/null || echo '{}'"
            )
            return json.loads(output) if output else None
        except Exception as e:
            logger.error(f"Failed to get pose: {e}")
            return None
    
    async def get_sensor_data(self) -> Optional[dict]:
        """Get sensor data (requires custom app)."""
        try:
            output = await self._run_shell_command(
                "cat /sdcard/loomo/sensors.json 2>/dev/null || echo '{}'"
            )
            return json.loads(output) if output else None
        except Exception as e:
            logger.error(f"Failed to get sensor data: {e}")
            return None
    
    async def get_ultrasonic_distance(self) -> Optional[float]:
        """Get ultrasonic distance."""
        try:
            output = await self._run_shell_command(
                "cat /sdcard/loomo/ultrasonic.txt 2>/dev/null || echo -1"
            )
            return float(output) if output else None
        except Exception as e:
            logger.error(f"Failed to get ultrasonic: {e}")
            return None
    
    async def get_camera_frame(self) -> Optional[bytes]:
        """Get camera frame via ADB screencap."""
        try:
            # Take screenshot
            await self._run_adb_command([
                "-s", self.device_id, "shell", 
                "screencap", "-p", "/sdcard/screen.png"
            ])
            # Pull screenshot
            await self._run_adb_command([
                "-s", self.device_id, "pull", 
                "/sdcard/screen.png", "/tmp/loomo_screen.png"
            ])
            
            with open("/tmp/loomo_screen.png", "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to get camera frame: {e}")
            return None
    
    async def speak(self, text: str) -> bool:
        """Make Loomo speak using TTS."""
        try:
            cmd = f"am startservice -a android.intent.action.SYNC " \
                  f"--es text '{text}' com.loomo.bridge/.TtsService"
            await self._run_shell_command(cmd)
            return True
        except Exception as e:
            logger.error(f"Failed to speak: {e}")
            return False
    
    async def play_sound(self, sound_file: str) -> bool:
        """Play sound file."""
        try:
            cmd = f"am start -a android.intent.action.VIEW " \
                  f"-d file:///sdcard/{sound_file} -t audio/wav"
            await self._run_shell_command(cmd)
            return True
        except Exception as e:
            logger.error(f"Failed to play sound: {e}")
            return False
    
    async def ping(self) -> bool:
        """Check if Loomo is responsive."""
        try:
            await self._run_shell_command("echo ping")
            return True
        except:
            return False
    
    async def start_camera_stream(self, callback):
        """Start camera stream (not implemented for ADB)."""
        logger.warning("Camera streaming not available via ADB")
        return False
    
    async def stop_camera_stream(self):
        """Stop camera stream."""
        pass
