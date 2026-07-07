#!/usr/bin/env python3
"""
Basic Loomo Control Example

This example demonstrates how to connect to and control a Segway Loomo robot
using the Loomo Bridge Python library.

Prerequisites:
- Loomo robot powered on and connected to WiFi
- ADB installed on this computer
- Loomo's IP address known
"""

import asyncio
import sys
import logging

# Add parent directory to path to import loomo_bridge
sys.path.insert(0, '/home/patrick/.openclaw/workspace/loomo-bridge')

from loomo_bridge import LoomoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run basic control demo."""
    
    # Configuration
    LOOMO_IP = "192.168.42.129"  # Change to your Loomo's IP
    CONNECTION_TYPE = "adb"  # Options: "adb", "ros", "websocket"
    
    # Initialize client
    loomo = LoomoClient(
        host=LOOMO_IP,
        connection_type=CONNECTION_TYPE
    )
    
    try:
        # Connect to Loomo
        logger.info(f"Connecting to Loomo at {LOOMO_IP}...")
        connected = await loomo.connect()
        
        if not connected:
            logger.error("Failed to connect to Loomo")
            return 1
        
        logger.info("Connected to Loomo!")
        
        # Get battery level
        battery = await loomo.get_battery_level()
        logger.info(f"Battery level: {battery}%")
        
        # Basic movement demo
        logger.info("Starting movement demo...")
        
        # Move forward
        logger.info("Moving forward...")
        await loomo.move_forward(speed=0.3, duration=2.0)
        await asyncio.sleep(0.5)
        
        # Turn left
        logger.info("Turning left...")
        await loomo.turn_left(angular_speed=0.5, duration=1.5)
        await asyncio.sleep(0.5)
        
        # Move forward again
        logger.info("Moving forward...")
        await loomo.move_forward(speed=0.3, duration=2.0)
        await asyncio.sleep(0.5)
        
        # Turn right
        logger.info("Turning right...")
        await loomo.turn_right(angular_speed=0.5, duration=1.5)
        await asyncio.sleep(0.5)
        
        # Stop
        logger.info("Stopping...")
        await loomo.stop()
        
        # Head/camera demo
        logger.info("Moving head...")
        await loomo.set_head_pose(yaw=30, pitch=-10)
        await asyncio.sleep(1.0)
        await loomo.set_head_pose(yaw=-30, pitch=10)
        await asyncio.sleep(1.0)
        await loomo.reset_head()
        
        # Get sensor data
        logger.info("Reading sensors...")
        ultrasonic = await loomo.get_ultrasonic_distance()
        logger.info(f"Ultrasonic distance: {ultrasonic} cm")
        
        # Speak
        logger.info("Speaking...")
        await loomo.speak("Hello, I am Loomo!")
        
        logger.info("Demo complete!")
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    finally:
        # Always disconnect
        logger.info("Disconnecting...")
        await loomo.disconnect()
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
