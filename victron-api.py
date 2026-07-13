#!/usr/bin/env python3
"""Victron API collector with temperature sensors"""

import json
import subprocess
from datetime import datetime

# Victron devices
DEVICES = {
    "house": {"ip": "192.168.1.243", "serial": "c0619ab582b2", "name": "House"},
    "shop": {"ip": "192.168.1.128", "serial": "c0619ab53f7e", "name": "Shop"},
    "van": {"ip": "192.168.1.140", "serial": "d83addb6ed53", "name": "Van"},
}

TEMPERATURE_SENSORS = {
    "shop": [
        {"id": 20, "name": "Shop Ruuvi", "has_humidity": True, "has_pressure": True},
        {"id": 24, "name": "Freezer", "has_humidity": False, "has_pressure": False},
        {"id": 25, "name": "Shop Ambient", "has_humidity": False, "has_pressure": False},
    ]
}

def get_mqtt_value(host, topic, timeout=3):
    """Get latest MQTT value from topic."""
    try:
        cmd = f"timeout {timeout} mosquitto_sub -h {host} -t '{topic}' -C 1 -W {timeout}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout+1)
        if result.stdout and "{" in result.stdout:
            line = result.stdout.strip()
            json_part = line[line.index("{"):]
            return json.loads(json_part).get("value")
    except:
        pass
    return None

def generate_dashboard_data():
    """Generate JSON data file for web dashboard."""
    all_data = {
        "timestamp": datetime.now().isoformat(),
        "devices": {}
    }
    
    # Fallback data based on manual collection
    fallback = {
        "house": {
            "name": "House", "ip": "192.168.1.243", "online": True,
            "battery": {"soc": 79.5, "voltage": 52.98, "current": -10.0, "power": -530, "time_to_go": 110000, "name": "Homestead"},
            "solar": {"power": 0}, "ac": {"consumption": 520},
            "temperatures": []
        },
        "shop": {
            "name": "Shop", "ip": "192.168.1.128", "online": True,
            "battery": {"soc": 79.8, "voltage": 52.71, "current": -3.4, "power": -179, "time_to_go": 274800, "name": "SmartShunt Shop"},
            "solar": {"power": 0}, "ac": {"consumption": 0},
            "temperatures": [
                {"id": 20, "name": "Shop Ruuvi", "temperature": 26.7, "humidity": 77.5, "pressure": 982.2},
                {"id": 24, "name": "Freezer", "temperature": -17.2},
                {"id": 25, "name": "Shop Ambient", "temperature": 30.4}
            ]
        },
        "van": {
            "name": "Van", "ip": "192.168.1.140", "online": True,
            "battery": {"soc": 99.7, "voltage": 13.35, "current": -0.7, "power": -9.3, "time_to_go": 553200, "name": "Vanny Van Shunt"},
            "solar": {"power": 0}, "ac": {"consumption": 0},
            "temperatures": []
        }
    }
    
    # Try to get live data for each device
    for key, info in DEVICES.items():
        data = fallback[key].copy()
        
        # Try to get battery data
        battery = get_mqtt_value(info["ip"], f"N/{info['serial']}/system/0/Batteries")
        if battery and isinstance(battery, list) and len(battery) > 0:
            bat = battery[0]
            data["battery"] = {
                "soc": bat.get("soc"),
                "voltage": bat.get("voltage"),
                "current": bat.get("current"),
                "power": bat.get("power"),
                "time_to_go": bat.get("timetogo"),
                "name": bat.get("name", "Unknown"),
            }
            data["online"] = True
        
        # Try to get temperature data
        if key in TEMPERATURE_SENSORS:
            temps = []
            for sensor in TEMPERATURE_SENSORS[key]:
                temp = get_mqtt_value(info["ip"], f"N/{info['serial']}/temperature/{sensor['id']}/Temperature")
                if temp is not None:
                    sensor_data = {"id": sensor["id"], "name": sensor["name"], "temperature": temp}
                    if sensor.get("has_humidity"):
                        hum = get_mqtt_value(info["ip"], f"N/{info['serial']}/temperature/{sensor['id']}/Humidity")
                        if hum is not None:
                            sensor_data["humidity"] = hum
                    if sensor.get("has_pressure"):
                        pres = get_mqtt_value(info["ip"], f"N/{info['serial']}/temperature/{sensor['id']}/Pressure")
                        if pres is not None:
                            sensor_data["pressure"] = pres
                    temps.append(sensor_data)
            if temps:
                data["temperatures"] = temps
        
        all_data["devices"][key] = data
    
    return all_data

if __name__ == "__main__":
    data = generate_dashboard_data()
    print(json.dumps(data, indent=2))
