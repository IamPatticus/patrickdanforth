#!/usr/bin/env python3
"""Victron API collector using curl + MQTT hybrid"""

import json
import subprocess
from datetime import datetime

# Known data from manual collection - update these periodically
# This serves as fallback when MQTT is slow

def collect_device_data(device_key, device_info):
    """Try MQTT first, then use fallback."""
    host = device_info["ip"]
    serial = device_info["serial"]
    
    data = {
        "name": device_info["name"],
        "ip": host,
        "last_update": datetime.now().isoformat(),
        "online": False,
        "battery": {},
        "solar": {},
        "ac": {},
    }
    
    # Quick MQTT check (2 second timeout max)
    try:
        cmd = f"timeout 2 mosquitto_sub -h {host} -t 'N/{serial}/system/0/Batteries' -C 1 -W 2"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
        if result.stdout and "value" in result.stdout:
            line = result.stdout.strip()
            json_part = line[line.index("{"):]
            bat = json.loads(json_part)["value"]
            if isinstance(bat, list) and len(bat) > 0:
                b = bat[0]
                data["battery"] = {
                    "soc": b.get("soc"),
                    "voltage": b.get("voltage"),
                    "current": b.get("current"),
                    "power": b.get("power"),
                    "time_to_go": b.get("timetogo"),
                    "name": b.get("name", "Unknown"),
                }
                data["online"] = True
    except:
        pass
    
    return data

def generate_dashboard_data():
    all_data = {
        "timestamp": datetime.now().isoformat(),
        "devices": {}
    }
    
    # Hardcoded fallback data based on our manual collection
    # This ensures the page always works even if devices are offline
    fallback = {
        "house": {
            "name": "House", "ip": "192.168.1.243", "online": True,
            "battery": {"soc": 79.5, "voltage": 52.98, "current": -10.0, "power": -530, "time_to_go": 110000, "name": "Homestead"},
            "solar": {"power": 0}, "ac": {"consumption": 520}
        },
        "shop": {
            "name": "Shop", "ip": "192.168.1.128", "online": True,
            "battery": {"soc": 79.8, "voltage": 52.71, "current": -3.4, "power": -179, "time_to_go": 274800, "name": "SmartShunt Shop"},
            "solar": {"power": 0}, "ac": {"consumption": 0}
        },
        "van": {
            "name": "Van", "ip": "192.168.1.140", "online": True,
            "battery": {"soc": 99.7, "voltage": 13.35, "current": -0.7, "power": -9.3, "time_to_go": 553200, "name": "Vanny Van Shunt"},
            "solar": {"power": 0}, "ac": {"consumption": 0}
        }
    }
    
    # Try to get live data for each device
    DEVICES = {
        "house": {"ip": "192.168.1.243", "serial": "c0619ab582b2", "name": "House"},
        "shop": {"ip": "192.168.1.128", "serial": "c0619ab53f7e", "name": "Shop"},
        "van": {"ip": "192.168.1.140", "serial": "d83addb6ed53", "name": "Van"},
    }
    
    for key, info in DEVICES.items():
        live = collect_device_data(key, info)
        if live.get("online") and live.get("battery"):
            # Merge live data with fallback
            all_data["devices"][key] = {**fallback[key], **live}
        else:
            # Use fallback with offline flag
            all_data["devices"][key] = fallback[key]
            all_data["devices"][key]["online"] = False
    
    return all_data

if __name__ == "__main__":
    data = generate_dashboard_data()
    print(json.dumps(data, indent=2))
