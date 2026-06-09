#!/usr/bin/env python3
# MPPT telemetry collector: subscribes to each device's MQTT-over-WebSocket feed
# and writes a JSON cache for the Mission Control dashboard.

import json
import time
import threading
from collections import deque, defaultdict
from pathlib import Path

import paho.mqtt.client as mqtt

OUT = Path('/home/patrick/.openclaw/workspace/services/mission-control/mppt-data.json')
HOSTS = {
    'house': '192.168.1.121',
    'garage': '192.168.1.243',
}

# Keep short rolling history (max points per metric)
HISTORY_LEN = 60
lock = threading.Lock()
state = {
    'house': {'metrics': defaultdict(lambda: None), 'history': defaultdict(lambda: deque(maxlen=HISTORY_LEN))},
    'garage': {'metrics': defaultdict(lambda: None), 'history': defaultdict(lambda: deque(maxlen=HISTORY_LEN))},
}

def safe_parse_payload(payload_bytes):
    try:
        s = payload_bytes.decode('utf-8')
        return json.loads(s)
    except Exception:
        # try numeric
        try:
            return float(payload_bytes)
        except Exception:
            return None

# Heuristic mapping of topic -> metric name
def topic_to_metric(topic):
    # lowercase for matching
    t = topic.lower()
    # ignore system topics
    if '/system/' in t:
        return None
    # dc (solar) indicators
    if '/dc/' in t or '/pv/' in t:
        if t.endswith('voltage'):
            return 'pv_voltage'
        if t.endswith('current'):
            return 'pv_current'
        if t.endswith('power'):
            return 'pv_power'
        if 'energy' in t:
            return 'pv_energy'
        # fallback
        return 'pv_'+t.split('/')[-1]
    # ac output
    if '/ac/' in t or '/ac/out' in t or '/inverter/' in t:
        if t.endswith('voltage'):
            return 'ac_voltage'
        if t.endswith('current'):
            return 'ac_current'
        if t.endswith('power'):
            return 'ac_power'
        return 'ac_'+t.split('/')[-1]
    # last-resort: look for keywords
    if 'voltage' in t:
        return 'voltage'
    if 'current' in t:
        return 'current'
    if 'power' in t:
        return 'power'
    return None


def make_on_message(name):
    def on_message(client, userdata, msg):
        val = safe_parse_payload(msg.payload)
        metric = topic_to_metric(msg.topic)
        ts = int(time.time())
        if metric is None:
            # store raw topic value generically
            metric = 'raw_'+msg.topic.replace('/', '_')
        with lock:
            # if payload is dict with 'value' key, prefer that
            if isinstance(val, dict) and 'value' in val:
                v = val['value']
            else:
                v = val
            try:
                # keep float numbers where possible
                if isinstance(v, (int, float)):
                    state[name]['metrics'][metric] = float(v)
                    state[name]['history'][metric].append({'t': ts, 'v': float(v)})
                else:
                    state[name]['metrics'][metric] = v
            except Exception:
                state[name]['metrics'][metric] = v
    return on_message


def make_on_connect(name):
    def on_connect(client, userdata, flags, rc):
        # subscribe broadly; device topics typically live under N/<id>/...
        client.subscribe('#')
    return on_connect


def start_client(name, host):
    client = mqtt.Client(transport='websockets')
    client.on_connect = make_on_connect(name)
    client.on_message = make_on_message(name)
    client.ws_set_options(path='/websocket-mqtt')
    # connect on port 80 (websocket)
    client.connect(host, 80, keepalive=60)
    client.loop_start()
    return client


def writer_loop():
    while True:
        out = {'updated': int(time.time()), 'devices': {}}
        with lock:
            for name in state:
                out['devices'][name] = {
                    'metrics': dict(state[name]['metrics']),
                    'history': {k: list(v) for k, v in state[name]['history'].items()}
                }
        try:
            OUT.write_text(json.dumps(out))
        except Exception as e:
            print('write error', e)
        time.sleep(5)


def main():
    clients = []
    for name, host in HOSTS.items():
        try:
            clients.append(start_client(name, host))
        except Exception as e:
            print('client start failed for', name, host, e)
    t = threading.Thread(target=writer_loop, daemon=True)
    t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for c in clients:
            try:
                c.loop_stop()
                c.disconnect()
            except Exception:
                pass

if __name__ == '__main__':
    main()
