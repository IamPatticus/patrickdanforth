#!/usr/bin/env python3
"""
Solar Snapshot Generator - Polls Cerbo GX devices via Modbus TCP
Updates solar-snapshot.json every 15 minutes

Victron Modbus-TCP Register Map (Unit 100 = System):
- 840: Battery SOC (scale 0.1, %)
- 841: Battery power (scale 1, signed, W) - negative = discharging
- 842: Battery voltage (scale 0.01, signed, V)
- 843: Battery current (scale 0.1, signed, A)
- 844: Battery temperature (scale 0.1, signed, °C)
- 845-846: Consumed Ah / Time to go
- 826: PV power (scale 1, unsigned, W) - AC coupled
- 810: Grid L1 power (scale 1, signed, W) - positive = import, negative = export
- 832: AC loads L1 power (scale 1, signed, W)
"""

import json
import struct
import socket
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Device configurations
CERBOS = {
    'house': {'ip': '192.168.1.243', 'port': 502, 'name': 'House'},
    'shop': {'ip': '192.168.1.128', 'port': 502, 'name': 'Shop/Garage'},
}

OUTPUT_FILE = Path('/home/patrick/.openclaw/workspace/solar-snapshot.json')
SITE_FILE = Path('/home/patrick/.openclaw/workspace/snapshot.json')  # For patrickdanforth.com

# Modbus register mappings for Victron system device (Unit 100)
REGISTERS = {
    'battery_soc': {'addr': 840, 'scale': 0.1, 'signed': False, 'unit': 100},
    'battery_power': {'addr': 841, 'scale': 1, 'signed': True, 'unit': 100},
    'battery_voltage': {'addr': 842, 'scale': 0.01, 'signed': True, 'unit': 100},
    'battery_current': {'addr': 843, 'scale': 0.1, 'signed': True, 'unit': 100},
    'battery_temp': {'addr': 844, 'scale': 0.1, 'signed': True, 'unit': 100},
    'pv_power': {'addr': 826, 'scale': 1, 'signed': False, 'unit': 100},  # AC coupled PV
    'grid_power': {'addr': 810, 'scale': 1, 'signed': True, 'unit': 100},
    'ac_loads': {'addr': 832, 'scale': 1, 'signed': True, 'unit': 100},
}


def read_modbus_register(ip: str, port: int, unit: int, addr: int, count: int = 1) -> Optional[list]:
    """Read holding registers from Modbus TCP device."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((ip, port))
        
        # Build Modbus TCP request
        transaction_id = 1
        protocol_id = 0
        length = 6
        function_code = 3  # Read holding registers
        
        request = struct.pack('>HHHBBHH', transaction_id, protocol_id, length, unit, function_code, addr, count)
        sock.send(request)
        
        # Receive response
        response = sock.recv(256)
        sock.close()
        
        if len(response) < 9:
            return None
        
        # Parse response
        byte_count = response[8]
        data = response[9:9 + byte_count]
        
        # Convert to registers (16-bit unsigned)
        registers = []
        for i in range(0, len(data), 2):
            registers.append(struct.unpack('>H', data[i:i+2])[0])
        
        return registers
    except Exception as e:
        print(f"  Modbus read error: {e}")
        return None


def decode_value(raw_val: int, scale: float, signed: bool) -> float:
    """Decode register value with scaling."""
    if signed and raw_val > 32767:
        raw_val = raw_val - 65536
    return raw_val * scale


def poll_cerbo(config: Dict[str, Any]) -> Dict[str, Any]:
    """Poll a Cerbo device and return parsed data."""
    ip = config['ip']
    port = config['port']
    name = config['name']
    
    print(f"\nPolling {name} at {ip}:{port}...")
    
    result = {'online': False}
    
    # Check if device is reachable
    try:
        test = read_modbus_register(ip, port, 100, 840, 1)
        if test is None:
            print(f"  ❌ Device unreachable")
            return result
        result['online'] = True
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        return result
    
    # Read all configured registers
    for field, reg_config in REGISTERS.items():
        try:
            data = read_modbus_register(ip, port, reg_config['unit'], reg_config['addr'])
            if data:
                value = decode_value(data[0], reg_config['scale'], reg_config['signed'])
                result[field] = value
                print(f"  {field}: {value}")
            else:
                result[field] = None
                print(f"  {field}: None (no response)")
        except Exception as e:
            print(f"  {field}: Error - {e}")
            result[field] = None
    
    return result


def discover_solar_chargers(ip: str, port: int) -> list:
    """Discover solar charger units and their power output."""
    chargers = []
    # Solar chargers typically start at unit 226 or 227 on Cerbo GX
    for unit in range(220, 256):
        try:
            # Try to read PV power at register 789
            data = read_modbus_register(ip, port, unit, 789)
            if data and data[0] > 0 and data[0] < 30000:
                # Also try to get name/product ID at register 800
                name_data = read_modbus_register(ip, port, unit, 800, 8)
                chargers.append({
                    'unit': unit,
                    'power': data[0],
                    'name': f'Charger-{unit}'
                })
        except:
            pass
    return chargers


def build_snapshot(house_data: Dict, shop_data: Dict) -> Dict[str, Any]:
    """Build the solar snapshot in the expected format."""
    now = datetime.now()
    timestamp = now.timestamp()
    
    # Determine battery state
    house_batt_power = house_data.get('battery_power') or 0
    house_batt_state = "CHARGING" if house_batt_power > 0 else "DISCHARGING"
    
    shop_batt_power = shop_data.get('battery_power') or 0
    shop_batt_state = "CHARGING" if shop_batt_power > 0 else "DISCHARGING"
    
    snapshot = {
        "timestamp": timestamp,
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "weather": {
            "temperature": None,
            "condition": None,
            "humidity": None
        },
        "house": {
            "pv_power_w": house_data.get('pv_power') or 0,
            "battery_soc_pct": house_data.get('battery_soc') or 0,
            "battery_power_w": house_batt_power,
            "battery_voltage_v": house_data.get('battery_voltage') or 0,
            "battery_current_a": house_data.get('battery_current') or 0,
            "battery_state": house_batt_state,
            "battery_time_to_go_h": 0.0,
            "battery_amphours": 0.0,
            "consumption_l1_w": house_data.get('ac_loads') or 0,
            "grid_l1_w": house_data.get('grid_power') or 0,
            "system_power_w": house_batt_power,
            "ac_loads_w": house_data.get('ac_loads') or 0,
            "dc_loads_w": 0.0,
            "inverter_output_w": abs(house_batt_power),
            "inverter_state": "Inverting" if house_data.get('online') else "Off",
            "inverter_dc_power_w": house_batt_power,
            "inverter_apparent_power_va": abs(house_batt_power),
            "inverter_output_voltage_v": 0.0,
            "inverter_output_frequency_hz": 0.0,
            "inverter_lifetime_kwh": 0.0,
            "solar_production_w": house_data.get('pv_power') or 0,
            "bus_charge_power_w": house_batt_power,
            "bus_charge_current_a": house_data.get('battery_current') or 0,
            "dc_pv_current_a": 0.0,
            "dc_pv_power_w": house_data.get('pv_power') or 0,
            "homestead_power_w": house_batt_power,
            "homestead_soc_pct": house_data.get('battery_soc') or 0,
            "homestead_charged_kwh": 0.0,
            "homestead_discharged_kwh": 0.0,
            "house_dc_battery_power_w": house_batt_power
        },
        "shop": {
            "battery_soc_pct": shop_data.get('battery_soc') or 0,
            "power_w": abs(shop_batt_power),
            "dc_bus_voltage_v": shop_data.get('battery_voltage') or 0,
            "dc_bus_current_a": shop_data.get('battery_current') or 0,
            "consumed_ah": 0.0,
            "time_to_go_s": 0.0,
            "battery_temp_f": ((shop_data.get('battery_temp') or 0) * 1.8 + 32) if shop_data.get('battery_temp') else 0,
            "charged_energy_kwh": 0.0,
            "discharged_energy_kwh": 0.0,
            "solar_production_w": shop_data.get('pv_power') or 0,
            "yield_today_kwh": 0.0,
            "state": shop_batt_state
        },
        "totals": {
            "total_solar_w": (house_data.get('pv_power') or 0) + (shop_data.get('pv_power') or 0),
            "total_battery_soc": ((house_data.get('battery_soc') or 0) + (shop_data.get('battery_soc') or 0)) / 2,
            "total_consumption_w": (house_data.get('ac_loads') or 0) + abs(shop_batt_power),
            "house_online": house_data.get('online', False),
            "shop_online": shop_data.get('online', False)
        },
        "raw_data": {
            "house": {k: v for k, v in house_data.items() if k != 'online'},
            "shop": {k: v for k, v in shop_data.items() if k != 'online'}
        }
    }
    
    return snapshot


def main():
    """Main entry point."""
    print(f"\n{'='*60}")
    print(f"Solar Snapshot Generator - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Poll both devices
    house_data = poll_cerbo(CERBOS['house'])
    shop_data = poll_cerbo(CERBOS['shop'])
    
    # Build snapshot
    snapshot = build_snapshot(house_data, shop_data)
    
    # Write to files
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    with open(SITE_FILE, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ Snapshots written to:")
    print(f"   {OUTPUT_FILE}")
    print(f"   {SITE_FILE}")
    
    print(f"\n{'='*60}")
    print(f"✅ Snapshots written to: {OUTPUT_FILE} and {SITE_FILE}")
    print(f"\nSummary:")
    print(f"  House: SOC={snapshot['house']['battery_soc_pct']:.1f}% | PV={snapshot['house']['pv_power_w']:.0f}W | Load={snapshot['house']['ac_loads_w']:.0f}W | Grid={snapshot['house']['grid_l1_w']:.0f}W")
    print(f"  Shop:  SOC={snapshot['shop']['battery_soc_pct']:.1f}% | PV={snapshot['shop']['solar_production_w']:.0f}W")
    print(f"  Total Solar: {snapshot['totals']['total_solar_w']:.0f}W")
    print(f"  House Online: {'✅' if snapshot['totals']['house_online'] else '❌'}")
    print(f"  Shop Online: {'✅' if snapshot['totals']['shop_online'] else '❌'}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
