#!/usr/bin/env python3
import json
import os
import re
import time
from pathlib import Path

import paho.mqtt.client as mqtt

OUTPUT = Path("/var/www/venus/venus-mqtt.json")

STATE = {
    "battery_voltage": None,
    "battery_current": None,
    "battery_power": None,
    "solar_voltage": None,
    "time_since_full": None,
    "heartbeat": None,
    "updated": None,
}

TOPICS = [
    "N/+/battery/+/Dc/0/Voltage",
    "N/+/battery/+/Dc/0/Current",
    "N/+/battery/+/Dc/0/Power",
    "N/+/battery/+/History/TimeSinceLastFullCharge",
    "N/+/solarcharger/+/Dc/0/Voltage",
    "N/+/heartbeat",
]


def parse_value(payload: bytes):
    try:
        data = json.loads(payload.decode("utf-8"))
    except Exception:
        return None
    if isinstance(data, dict):
        return data.get("value")
    return None


def update_field(topic: str, value):
    if value is None:
        return False

    if re.search(r"/battery/\d+/Dc/0/Voltage$", topic):
        STATE["battery_voltage"] = float(value)
        return True
    if re.search(r"/battery/\d+/Dc/0/Current$", topic):
        STATE["battery_current"] = float(value)
        return True
    if re.search(r"/battery/\d+/Dc/0/Power$", topic):
        STATE["battery_power"] = float(value)
        return True
    if re.search(r"/battery/\d+/History/TimeSinceLastFullCharge$", topic):
        STATE["time_since_full"] = int(value)
        return True
    if re.search(r"/solarcharger/\d+/Dc/0/Voltage$", topic):
        voltage = float(value)
        STATE["solar_voltage"] = voltage
        if STATE["battery_voltage"] is None:
            STATE["battery_voltage"] = voltage
        return True
    if topic.endswith("/heartbeat"):
        STATE["heartbeat"] = int(value)
        return True
    return False


def write_state():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUTPUT.with_suffix(".tmp")
    STATE["updated"] = int(time.time())
    tmp.write_text(json.dumps(STATE, sort_keys=True, separators=(",", ":")))
    os.replace(tmp, OUTPUT)


def on_connect(client, userdata, flags, rc, properties=None):
    for topic in TOPICS:
        client.subscribe(topic, qos=0)


def on_message(client, userdata, msg):
    value = parse_value(msg.payload)
    changed = update_field(msg.topic, value)
    if changed:
        write_state()


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="venus-mqtt-bridge")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
