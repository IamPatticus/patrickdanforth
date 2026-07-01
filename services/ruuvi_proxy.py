#!/usr/bin/env python3
"""MQTT-to-HTTP proxy for Ruuvi sensor data from Venus OS.

Subscribes to the local Venus OS MQTT broker (192.168.1.140:1883),
caches the latest temperature/humidity/pressure values, and exposes
them as JSON on /ruuvi.
"""
import json
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

import paho.mqtt.client as mqtt

VENUS_HOST = "192.168.1.140"
VENUS_PORT = 1883
PORTAL_ID = "d83addb6ed53"
TOPIC_PREFIX = f"N/{PORTAL_ID}/temperature/20/"
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 8787

STATE = {
    "temperature": None,
    "humidity": None,
    "pressure": None,
    "accel_x": None,
    "accel_y": None,
    "accel_z": None,
    "seq_no": None,
    "updated_at": None,
    "connected": False,
}
LOCK = threading.Lock()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        with LOCK:
            STATE["connected"] = True
        client.subscribe("#")
    else:
        with LOCK:
            STATE["connected"] = False


def on_disconnect(client, userdata, rc):
    with LOCK:
        STATE["connected"] = False


def on_message(client, userdata, msg):
    suffix = msg.topic.replace(TOPIC_PREFIX, "")
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        value = payload.get("value")
    except Exception:
        return

    with LOCK:
        now = datetime.now(timezone.utc).isoformat()
        if suffix == "Temperature":
            STATE["temperature"] = value
        elif suffix == "Humidity":
            STATE["humidity"] = value
        elif suffix == "Pressure":
            STATE["pressure"] = value
        elif suffix == "AccelX":
            STATE["accel_x"] = value
        elif suffix == "AccelY":
            STATE["accel_y"] = value
        elif suffix == "AccelZ":
            STATE["accel_z"] = value
        elif suffix == "SeqNo":
            STATE["seq_no"] = value
        STATE["updated_at"] = now


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if self.path not in ("/ruuvi", "/"):
            self.send_error(404)
            return

        with LOCK:
            body = json.dumps(STATE, indent=2).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)


def mqtt_loop():
    client = mqtt.Client(client_id=f"ruuvi-proxy-{int(time.time())}")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(VENUS_HOST, VENUS_PORT, 60)
    client.loop_forever(retry_first_connection=True)


def main():
    mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
    mqtt_thread.start()

    server = HTTPServer((LISTEN_HOST, LISTEN_PORT), Handler)
    print(f"Ruuvi proxy listening on http://{LISTEN_HOST}:{LISTEN_PORT}/ruuvi")
    server.serve_forever()


if __name__ == "__main__":
    main()
