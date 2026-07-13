#!/usr/bin/env python3
"""Victron API collector - fast version"""

import json
import subprocess
from datetime import datetime

DEVICES = {
    "house": {"ip": "192.168.1.243", "serial": "c0619ab582b2", "name": "House"},
    "shop": {"ip": "192.168.1.128", "serial": "c0619ab53f7e", "name": "Shop"},
    "van": {"ip": "192.168.1.140", "serial": "d83addb6ed53", "name": "Van"},
}

def get_mqtt_value(host, topic, timeout=2):
    """Get latest MQTT value from topic with short timeout."""
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

def get_battery_data(ip, serial):
    """Get battery data quickly."""
    # Try the main battery topic first
    battery = get_mqtt_value(ip, f"N/{serial}/system/0/Batteries", timeout=2)
    if battery and isinstance(battery, list) and len(battery) > 0:
        bat = battery[0]
        return {
            "soc": bat.get("soc"),
            "voltage": bat.get("voltage"),
            "current": bat.get("current"),
            "power": bat.get("power"),
            "time_to_go": bat.get("timetogo"),
            "name": bat.get("name", "Unknown"),
        }
    
    # Fallback: try individual battery topics
    soc = get_mqtt_value(ip, f"N/{serial}/system/0/Dc/Battery/Soc", timeout=1)
    if soc is not None:
        voltage = get_mqtt_value(ip, f"N/{serial}/system/0/Dc/Battery/Voltage", timeout=1)
        current = get_mqtt_value(ip, f"N/{serial}/system/0/Dc/Battery/Current", timeout=1)
        power = get_mqtt_value(ip, f"N/{serial}/system/0/Dc/Battery/Power", timeout=1)
        return {
            "soc": soc,
            "voltage": voltage,
            "current": current,
            "power": power,
            "name": "Battery"
        }
    
    return None

def discover_temperatures(ip, serial):
    """Discover temperature sensors quickly."""
    temps = []
    # Only check IDs 20-25 (common range)
    for sensor_id in range(20, 26):
        temp = get_mqtt_value(ip, f"N/{serial}/temperature/{sensor_id}/Temperature", timeout=1)
        if temp is not None:
            name = get_mqtt_value(ip, f"N/{serial}/temperature/{sensor_id}/CustomName", timeout=1)
            if not name:
                name = f"Sensor {sensor_id}"
            
            sensor_data = {"id": sensor_id, "name": name, "temperature": temp}
            
            humidity = get_mqtt_value(ip, f"N/{serial}/temperature/{sensor_id}/Humidity", timeout=1)
            if humidity is not None:
                sensor_data["humidity"] = humidity
            
            pressure = get_mqtt_value(ip, f"N/{serial}/temperature/{sensor_id}/Pressure", timeout=1)
            if pressure is not None:
                sensor_data["pressure"] = pressure
            
            temps.append(sensor_data)
    
    return temps

def generate_dashboard_data():
    """Generate JSON data for web dashboard."""
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
        
        # Get battery data (quick timeout)
        battery = get_battery_data(info["ip"], info["serial"])
        if battery:
            data["battery"] = battery
            data["online"] = True
        
        # Get temperatures
        temps = discover_temperatures(info["ip"], info["serial"])
        if temps:
            data["temperatures"] = temps
            data["online"] = True
        
        all_data["devices"][key] = data
    
    return all_data

if __name__ == "__main__":
    data = generate_dashboard_data()
    print(json.dumps(data, indent=2))
