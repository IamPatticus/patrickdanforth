#!/usr/bin/env python3
"""Venus OS MQTT bridge for multiple Cerbo GX devices.

Reads Victron MQTT data from one or more Venus OS brokers, aggregates the
values into a single JSON file, and keeps it updated on every incoming message.

Output file is written to /var/www/venus/venus-mqtt.json by default.
"""

import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import paho.mqtt.client as mqtt

OUTPUT = Path(os.environ.get("VENUS_OUTPUT", "/var/www/venus/venus-mqtt.json"))

# List of Venus OS MQTT brokers to monitor.
# Each broker is a Cerbo GX device on the local network. The VRM Portal ID
# is learned from MQTT topic prefixes at runtime.
BROKERS = [
    {"host": "localhost", "port": 1883, "system": "house", "label": "homestead"},
    {"host": "192.168.1.140", "port": 1883, "system": "shop", "label": "tinker_town"},
]

# Topic patterns to subscribe to. '+' wildcards match portal ID and instance.
TOPICS = [
    # System overview (single source of truth)
    "N/+/system/0/Dc/Battery/Soc",
    "N/+/system/0/Dc/Battery/Voltage",
    "N/+/system/0/Dc/Battery/Current",
    "N/+/system/0/Dc/Battery/Power",
    "N/+/system/0/Dc/Battery/State",
    "N/+/system/0/Dc/Battery/TimeToGo",
    "N/+/system/0/Dc/Pv/Power",
    "N/+/system/0/Dc/Pv/Current",
    "N/+/system/0/Dc/InverterCharger/Power",
    "N/+/system/0/Dc/System/Power",
    "N/+/system/0/Ac/ConsumptionOnOutput/L1/Power",
    "N/+/system/0/Ac/ConsumptionOnInput/L1/Power",
    "N/+/system/0/Ac/Grid/L1/Power",
    "N/+/system/0/Ac/Genset/L1/Power",
    "N/+/system/0/Ac/ActiveIn/Source",
    "N/+/system/0/SystemState/State",
    # Battery service details
    "N/+/battery/+/Dc/0/Voltage",
    "N/+/battery/+/Dc/0/Current",
    "N/+/battery/+/Dc/0/Power",
    "N/+/battery/+/Soc",
    # Solar charger details
    "N/+/solarcharger/+/Dc/0/Voltage",
    "N/+/solarcharger/+/Dc/0/Current",
    "N/+/solarcharger/+/Dc/0/Power",
    "N/+/solarcharger/+/Yield/Power",
    "N/+/solarcharger/+/Yield/System",
    # VE.Bus inverter/charger details
    "N/+/vebus/+/Ac/Out/L1/Power",
    "N/+/vebus/+/Ac/ActiveIn/L1/Power",
    "N/+/vebus/+/Ac/ActiveIn/ActiveInput",
    "N/+/vebus/+/State",
    # Heartbeat and history
    "N/+/battery/+/History/TimeSinceLastFullCharge",
    "N/+/+/heartbeat",
]


@dataclass
class BrokerState:
    system: str
    label: str
    portal_id: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    last_seen: float = 0.0


STATE: dict[str, BrokerState] = {}
LAST_WRITE = 0.0
WRITE_COOLDOWN_S = 0.5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def parse_value(payload: bytes):
    try:
        data = json.loads(payload.decode("utf-8"))
    except Exception:
        return None
    if isinstance(data, dict):
        return data.get("value")
    return None


def identify_system(client) -> BrokerState | None:
    label = getattr(client, "_venus_label", None)
    if label is None:
        return None
    return STATE.get(label)


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        v = float(value)
        if v == -1 or v == -32768:  # common Victron invalid sentinel
            return None
        return v
    except (TypeError, ValueError):
        return None


def safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Field mapping
# ---------------------------------------------------------------------------
def update_field(state: BrokerState, topic: str, value: Any) -> bool:
    """Map a Victron MQTT topic to a field in this broker's data dict."""
    if value is None:
        return False

    changed = False
    system = state.system

    # Helper to set a value only when different.
    def set_key(key: str, v: Any):
        nonlocal changed
        if state.data.get(key) != v:
            state.data[key] = v
            changed = True

    # Portal ID detection from first segment
    m = re.match(r"N/([^/]+)/", topic)
    if m and state.portal_id != m.group(1):
        state.portal_id = m.group(1)
        changed = True

    # --- System battery overview ---
    if topic.endswith("/system/0/Dc/Battery/Soc"):
        set_key(f"{system}_soc_pct", safe_float(value))
    elif topic.endswith("/system/0/Dc/Battery/Voltage"):
        set_key(f"{system}_battery_voltage_v", safe_float(value))
    elif topic.endswith("/system/0/Dc/Battery/Current"):
        set_key(f"{system}_battery_current_a", safe_float(value))
    elif topic.endswith("/system/0/Dc/Battery/Power"):
        set_key(f"{system}_battery_power_w", safe_float(value))
    elif topic.endswith("/system/0/Dc/Battery/State"):
        set_key(f"{system}_battery_state", safe_int(value))
    elif topic.endswith("/system/0/Dc/Battery/TimeToGo"):
        set_key(f"{system}_battery_time_to_go_s", safe_int(value))

    # --- Solar ---
    elif topic.endswith("/system/0/Dc/Pv/Power"):
        set_key(f"{system}_pv_power_w", safe_float(value))
    elif topic.endswith("/system/0/Dc/Pv/Current"):
        set_key(f"{system}_pv_current_a", safe_float(value))

    # --- Inverter/Charger ---
    elif topic.endswith("/system/0/Dc/InverterCharger/Power"):
        set_key(f"{system}_inverter_charger_power_w", safe_float(value))
    elif topic.endswith("/system/0/Dc/System/Power"):
        set_key(f"{system}_dc_system_power_w", safe_float(value))

    # --- AC loads / grid ---
    elif topic.endswith("/system/0/Ac/ConsumptionOnOutput/L1/Power"):
        set_key(f"{system}_ac_output_load_w", safe_float(value))
    elif topic.endswith("/system/0/Ac/ConsumptionOnInput/L1/Power"):
        set_key(f"{system}_ac_input_load_w", safe_float(value))
    elif topic.endswith("/system/0/Ac/Grid/L1/Power"):
        set_key(f"{system}_grid_power_w", safe_float(value))
    elif topic.endswith("/system/0/Ac/Genset/L1/Power"):
        set_key(f"{system}_genset_power_w", safe_float(value))
    elif topic.endswith("/system/0/Ac/ActiveIn/Source"):
        set_key(f"{system}_ac_source", safe_int(value))

    # --- System state ---
    elif topic.endswith("/system/0/SystemState/State"):
        set_key(f"{system}_system_state", safe_int(value))

    # --- Battery service details ---
    elif re.search(r"/battery/\d+/Dc/0/Voltage$", topic):
        set_key(f"{system}_battery_service_voltage_v", safe_float(value))
    elif re.search(r"/battery/\d+/Dc/0/Current$", topic):
        set_key(f"{system}_battery_service_current_a", safe_float(value))
    elif re.search(r"/battery/\d+/Dc/0/Power$", topic):
        set_key(f"{system}_battery_service_power_w", safe_float(value))
    elif re.search(r"/battery/\d+/Soc$", topic):
        set_key(f"{system}_battery_service_soc_pct", safe_float(value))
    elif re.search(r"/battery/\d+/History/TimeSinceLastFullCharge$", topic):
        set_key(f"{system}_time_since_full_s", safe_int(value))

    # --- Solar charger details ---
    elif re.search(r"/solarcharger/\d+/Dc/0/Voltage$", topic):
        set_key(f"{system}_solar_charger_voltage_v", safe_float(value))
    elif re.search(r"/solarcharger/\d+/Dc/0/Current$", topic):
        set_key(f"{system}_solar_charger_current_a", safe_float(value))
    elif re.search(r"/solarcharger/\d+/Dc/0/Power$", topic):
        set_key(f"{system}_solar_charger_power_w", safe_float(value))
    elif re.search(r"/solarcharger/\d+/Yield/Power$", topic):
        inst = re.search(r"/solarcharger/(\d+)/Yield/Power$", topic)
        if inst:
            inst_key = f"{system}_solarcharger_{inst.group(1)}_yield_power_w"
            set_key(inst_key, safe_float(value))
        changed = True
    elif re.search(r"/solarcharger/\d+/Yield/System$", topic):
        inst = re.search(r"/solarcharger/(\d+)/Yield/System$", topic)
        if inst:
            inst_key = f"{system}_solarcharger_{inst.group(1)}_yield_total_kwh"
            set_key(inst_key, safe_float(value))
        changed = True

    # --- VE.Bus ---
    elif re.search(r"/vebus/\d+/Ac/Out/L1/Power$", topic):
        set_key(f"{system}_vebus_ac_out_power_w", safe_float(value))
    elif re.search(r"/vebus/\d+/Ac/ActiveIn/L1/Power$", topic):
        set_key(f"{system}_vebus_ac_in_power_w", safe_float(value))
    elif re.search(r"/vebus/\d+/Ac/ActiveIn/ActiveInput$", topic):
        set_key(f"{system}_vebus_active_input", safe_int(value))
    elif re.search(r"/vebus/\d+/State$", topic):
        set_key(f"{system}_vebus_state", safe_int(value))

    # --- Heartbeat ---
    elif topic.endswith("/heartbeat"):
        set_key(f"{system}_heartbeat", safe_int(value))
        state.last_seen = time.time()

    return changed


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def aggregate() -> dict[str, Any]:
    """Merge per-broker data into the final JSON output."""
    merged: dict[str, Any] = {"updated": int(time.time())}
    for label, state in STATE.items():
        for key, value in state.data.items():
            merged[key] = value
        merged[f"{state.system}_portal_id"] = state.portal_id
        merged[f"{state.system}_last_seen_s"] = int(time.time() - state.last_seen) if state.last_seen else None

    # Sum solar charger yield power across all instances per system
    for system in ("house", "shop"):
        total = 0.0
        for key, value in merged.items():
            if key.startswith(f"{system}_solarcharger_") and key.endswith("_yield_power_w"):
                total += value or 0.0
        if total > 0:
            merged[f"{system}_solar_charger_yield_power_w"] = round(total, 1)

    # Convenience totals
    house_pv = merged.get("house_pv_power_w")
    shop_pv = merged.get("shop_pv_power_w")
    if house_pv is not None and shop_pv is not None:
        merged["total_pv_power_w"] = round(house_pv + shop_pv, 1)

    house_load = merged.get("house_ac_output_load_w") or merged.get("house_ac_input_load_w")
    shop_load = merged.get("shop_ac_output_load_w") or merged.get("shop_ac_input_load_w")
    if house_load is not None and shop_load is not None:
        merged["total_ac_load_w"] = round(house_load + shop_load, 1)

    # Battery state text mapping for house (the main system on serenity)
    battery_state_map = {
        0: "Idle", 1: "Charging", 2: "Discharging",
    }
    merged["battery_state_text"] = battery_state_map.get(merged.get("house_battery_state"), "Unknown")

    # System state text
    system_state_map = {
        0: "Off", 1: "Low power", 2: "VE.Bus fault", 3: "Bulk",
        4: "Absorption", 5: "Float", 6: "Storage", 7: "Equalize",
        8: "Passthru", 9: "Inverting", 10: "Assisting",
        256: "Discharging", 257: "Sustain",
    }
    merged["system_state_text"] = system_state_map.get(merged.get("house_system_state"), "Unknown")

    return merged


def write_state():
    global LAST_WRITE
    now = time.time()
    if now - LAST_WRITE < WRITE_COOLDOWN_S:
        return
    LAST_WRITE = now

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUTPUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(aggregate(), sort_keys=True, separators=(",", ":")))
    os.replace(tmp, OUTPUT)


# ---------------------------------------------------------------------------
# MQTT callbacks
# ---------------------------------------------------------------------------
def on_connect_factory(label: str):
    def on_connect(client, userdata, flags, rc, properties=None):
        reason = mqtt.error_string(rc) if rc != 0 else "OK"
        print(f"[{label}] connected: {reason}")
        for topic in TOPICS:
            client.subscribe(topic, qos=0)
    return on_connect


def on_message_factory(label: str):
    def on_message(client, userdata, msg):
        state = STATE.get(label)
        if state is None:
            return
        value = parse_value(msg.payload)
        changed = update_field(state, msg.topic, value)
        if changed:
            write_state()
    return on_message


def on_disconnect_factory(label: str):
    def on_disconnect(client, userdata, rc, properties=None):
        print(f"[{label}] disconnected: {mqtt.error_string(rc) if rc else 'clean'}")
    return on_disconnect


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    clients: list[mqtt.Client] = []

    for cfg in BROKERS:
        label = cfg["label"]
        STATE[label] = BrokerState(system=cfg["system"], label=label)

        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"venus-bridge-{label}-{int(time.time())}",
        )
        client._venus_label = label
        client.on_connect = on_connect_factory(label)
        client.on_message = on_message_factory(label)
        client.on_disconnect = on_disconnect_factory(label)
        try:
            client.connect(cfg["host"], cfg["port"], 60)
            client.loop_start()
            clients.append(client)
        except Exception as e:
            print(f"[{label}] connection failed: {e}")

    try:
        while True:
            time.sleep(1)
            # Periodic write in case values haven't changed but output is stale
            write_state()
    except KeyboardInterrupt:
        pass
    finally:
        for client in clients:
            client.loop_stop()
            client.disconnect()


if __name__ == "__main__":
    main()
