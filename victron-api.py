#!/usr/bin/env python3
"""Victron API collector with temperature sensors"""

import json
import subprocess
from datetime import datetime

DEVICES = {
    "house": {"ip": "192.168.1.243", "serial": "c0619ab582b2", "name": "House"},
    "shop": {"ip": "192.168.1.128", "serial": "c0619ab53f7e", "name": "Shop"},
    "van": {"ip": "192.168.1.140", "serial": "d83addb6ed53", "name": "Van"},
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

def discover_temperatures(ip, serial):
    """Discover all temperature sensors on a device."""
    temps = []
    # Try common sensor IDs (20-30)
    for sensor_id in range(20, 31):
        temp = get_mqtt_value(ip, f"N/{serial}/temperature/{sensor_id}/Temperature")
        if temp is not None:
            name = get_mqtt_value(ip, f"N/{serial}/temperature/{sensor_id}/CustomName")
            if not name:
                name = f"Sensor {sensor_id}"
            
            sensor_data = {"id": sensor_id, "name": name, "temperature": temp}
            
            # Check for additional data
            humidity = get_mqtt_value(ip, f"N/{serial}/temperature/{sensor_id}/Humidity")
            if humidity is not None:
                sensor_data["humidity"] = humidity
            
            pressure = get_mqtt_value(ip, f"N/{serial}/temperature/{sensor_id}/Pressure")
            if pressure is not None:
                sensor_data["pressure"] = pressure
            
            temps.append(sensor_data)
    
    return temps

def generate_dashboard_data():
    """Generate JSON data file for web dashboard."""
    all_data = {
        "timestamp": datetime.now().isoformat(),
        "devices": {}
    }
    
    for key, info in DEVICES.items():
        data = {
            "name": info["name"],
            "ip": info["ip"],
            "online": False,
            "battery": {},
            "solar": {},
            "ac": {},
            "temperatures": []
        }
        
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
        else:
            # Fallback: try to get basic battery info
            soc = get_mqtt_value(info["ip"], f"N/{info['serial']}/system/0/Dc/Battery/Soc")
            if soc is not None:
                data["online"] = True
                data["battery"] = {
                    "soc": soc,
                    "name": info["name"]
                }
        
        # Discover temperature sensors
        temps = discover_temperatures(info["ip"], info["serial"])
        if temps:
            data["temperatures"] = temps
            data["online"] = True
        
        all_data["devices"][key] = data
    
    return all_data

if __name__ == "__main__":
    data = generate_dashboard_data()
    print(json.dumps(data, indent=2))
