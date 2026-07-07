#!/usr/bin/env python3
"""
Loomo Discovery Tool

Scans the network to find Segway Loomo robots.
"""

import asyncio
import subprocess
import socket
import sys
from concurrent.futures import ThreadPoolExecutor
import argparse

# Common Loomo network patterns
COMMON_SUBNETS = [
    "192.168.42",      # Default Loomo hotspot subnet
    "192.168.1",     # Common home router
    "192.168.0",     # Common home router
    "10.0.0",        # Common corporate
    "10.0.1",        # Common corporate
]

LOOMO_PORTS = [5555, 5554]  # ADB ports


def check_host(ip: str, ports: list) -> dict:
    """Check if host is responsive on any of the ports."""
    result = {"ip": ip, "responsive": False, "ports": []}
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((ip, port))
            sock.close()
            result["responsive"] = True
            result["ports"].append(port)
        except:
            pass
    
    return result


async def scan_subnet(subnet: str, start: int = 1, end: int = 254) -> list:
    """Scan a subnet for responsive hosts."""
    print(f"Scanning {subnet}.x ...")
    
    ips = [f"{subnet}.{i}" for i in range(start, end + 1)]
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, check_host, ip, LOOMO_PORTS)
            for ip in ips
        ]
        results = await asyncio.gather(*futures)
    
    return [r for r in results if r["responsive"]]


async def discover_loomo():
    """Main discovery function."""
    print("=== Loomo Discovery Tool ===\n")
    
    found_devices = []
    
    for subnet in COMMON_SUBNETS:
        try:
            results = await scan_subnet(subnet)
            for r in results:
                print(f"Found device: {r['ip']} (ports: {r['ports']})")
                
                # Try to identify if it's Loomo
                if 5555 in r["ports"]:
                    print(f"  -> Potential Loomo (ADB port 5555 open)")
                    found_devices.append(r)
        except Exception as e:
            print(f"Error scanning {subnet}: {e}")
    
    print(f"\n=== Results ===")
    if found_devices:
        print(f"Found {len(found_devices)} potential Loomo(s):")
        for device in found_devices:
            print(f"  - {device['ip']}")
        print("\nTry connecting with:")
        print(f"  python examples/basic_control.py (after updating IP)")
        print(f"  or: adb connect {found_devices[0]['ip']}:5555")
    else:
        print("No Loomo found.")
        print("\nMake sure:")
        print("  1. Loomo is powered on")
        print("  2. Loomo is connected to the same network")
        print("  3. USB debugging is enabled on Loomo")
        print("  4. ADB over WiFi is enabled on Loomo")


async def test_connection(ip: str, port: int = 5555):
    """Test connection to a specific IP."""
    print(f"Testing connection to {ip}:{port}...")
    
    result = check_host(ip, [port])
    
    if result["responsive"]:
        print(f"✓ {ip}:{port} is responsive")
        
        # Try ADB connection
        try:
            proc = await asyncio.create_subprocess_exec(
                "adb", "connect", f"{ip}:{port}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            output = stdout.decode().strip()
            
            if "connected" in output.lower():
                print(f"✓ ADB connected: {output}")
                
                # Get device info
                proc = await asyncio.create_subprocess_exec(
                    "adb", "-s", f"{ip}:{port}", "shell", "getprop", "ro.product.model",
                    stdout=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                model = stdout.decode().strip()
                print(f"  Model: {model}")
                
                # Get battery
                proc = await asyncio.create_subprocess_exec(
                    "adb", "-s", f"{ip}:{port}", "shell", "dumpsys", "battery",
                    stdout=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                for line in stdout.decode().split("\n"):
                    if "level:" in line:
                        print(f"  {line.strip()}")
                        break
                
                return True
            else:
                print(f"✗ ADB failed: {output}")
                return False
                
        except Exception as e:
            print(f"✗ ADB error: {e}")
            return False
    else:
        print(f"✗ {ip}:{port} is not responsive")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover and connect to Loomo")
    parser.add_argument("--ip", help="Test specific IP address")
    parser.add_argument("--port", type=int, default=5555, help="ADB port (default: 5555)")
    parser.add_argument("--scan", action="store_true", help="Scan network for Loomo")
    
    args = parser.parse_args()
    
    if args.ip:
        asyncio.run(test_connection(args.ip, args.port))
    elif args.scan or len(sys.argv) == 1:
        asyncio.run(discover_loomo())
