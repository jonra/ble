import requests
import time
import json
from bleak import BleakScanner, BleakError
from datetime import datetime
import uuid
import socket
import subprocess
import asyncio
from requests.exceptions import ConnectionError
from m1 import manufacturer_codes_1
from m2 import manufacturer_codes_2
from m3 import manufacturer_codes_3
from m4 import manufacturer_codes_4
from m5 import manufacturer_codes_5
from m6 import manufacturer_codes_6
from m7 import manufacturer_codes_7
from kalman_filter import KalmanFilter

# Merge all manufacturer codes into a single dictionary
manufacturer_codes = {}
manufacturer_codes.update(manufacturer_codes_1)
manufacturer_codes.update(manufacturer_codes_2)
manufacturer_codes.update(manufacturer_codes_3)
manufacturer_codes.update(manufacturer_codes_4)
manufacturer_codes.update(manufacturer_codes_5)
manufacturer_codes.update(manufacturer_codes_6)
manufacturer_codes.update(manufacturer_codes_7)

# Kalman filter instance
kalman_filter = KalmanFilter(1, 1, 1)

# Function to categorize devices based on a pattern in their serial numbers
def categorize_device(name):
    if name and name.startswith("HRM"):  # Example pattern for Heart Rate Monitors
        return "Heart Rate Monitor"
    elif name and name.startswith("TMP"):  # Example pattern for Thermometers
        return "Thermometer"
    elif name and name.startswith("BPM"):  # Example pattern for Blood Pressure Monitors
        return "Blood Pressure Monitor"
    elif name and "ENVY" in name:  # Additional pattern for ENVY devices
        return "ENVY Device"
    elif name and "Samsung" in name:  # Additional pattern for Samsung devices
        return "Samsung Device"
    elif name and "Bose" in name:  # Additional pattern for Bose devices
        return "Bose Device"
    else:
        return "Unknown Device"

# Function to estimate distance from RSSI
def estimate_distance(rssi):
    tx_power = -59  # This is a common value, but it may vary
    if rssi == 0:
        return -1.0  # if we cannot determine accuracy, return -1.
    rssi = kalman_filter.update(rssi)
    ratio = rssi * 1.0 / tx_power
    if ratio < 1.0:
        return ratio ** 10
    else:
        return (0.89976 * (ratio ** 7.7095)) + 0.111

# Function to get the manufacturer name from manufacturer data
def get_manufacturer_name(manufacturer_data):
    if manufacturer_data:
        for code in manufacturer_data.keys():
            return manufacturer_codes.get(code, f"Unknown Manufacturer (Code: {code})")
    return "N/A"

# Function to get internet connection metadata
def get_connection_metadata():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    wifi_info = get_wifi_info()
    device_uuid = get_device_uuid()

    connection_metadata = {
        "hostname": hostname,
        "ip_address": ip_address,
        "network_name": wifi_info['ssid'] if wifi_info['ssid'] else "Unknown",
        "network_type": "Wi-Fi" if wifi_info['ssid'] else "Unknown",
        "mac_address": wifi_info['mac_address'] if wifi_info['mac_address'] else "Unknown",
        "signal_level": wifi_info['signal_level'] if wifi_info['signal_level'] else "Unknown",
        "device_uuid": device_uuid
    }
    return connection_metadata

# Function to get detailed Wi-Fi information
def get_wifi_info():
    wifi_info = {
        "ssid": None,
        "mac_address": None,
        "signal_level": None
    }
    try:
        result = subprocess.run(['iwconfig'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'ESSID' in line:
                wifi_info['ssid'] = line.split('ESSID:')[1].strip().strip('"')
            if 'Access Point' in line:
                wifi_info['mac_address'] = line.split('Access Point:')[1].strip()
            if 'Signal level' in line:
                wifi_info['signal_level'] = line.split('Signal level=')[1].split(' ')[0].strip()
    except Exception as e:
        print(f"Error retrieving Wi-Fi info: {e}")
    return wifi_info

# Function to get the Linux device UUID
def get_device_uuid():
    try:
        with open("/etc/machine-id", "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error retrieving device UUID: {e}")
        return "Unknown"

# Function to scan for devices and list them grouped by type, excluding Apple devices
async def scan_and_list_devices():
    try:
        devices = await BleakScanner.discover(timeout=10.0)  # Set a timeout of 10 seconds
    except BleakError as e:
        print(f"Error during Bluetooth scan: {e}")
        return

    flattened_devices = []

    for device in devices:
        advertisement_data = device.details.get("props", {})
        rssi = advertisement_data.get('RSSI', 'N/A')
        distance = estimate_distance(rssi) if isinstance(rssi, int) else 'N/A'
        manufacturer_data = advertisement_data.get("ManufacturerData", {})
        manufacturer_name = get_manufacturer_name(manufacturer_data)

        # Skip devices with specific manufacturer names or name patterns
        if manufacturer_name in ["Apple, Inc.", "Microsoft"] or \
                any(x in device.name for x in ["Microsoft", "Lynk", "Samsung"]):
            continue

        device_type = categorize_device(device.name)
        flattened_devices.append({
            "name": device.name,
            "address": device.address,
            "rssi": rssi,
            "distance": distance,
            "manufacturer": manufacturer_name,
            "uuid": str(uuid.uuid5(uuid.NAMESPACE_DNS, device.address)),  # Generate a unique UUID for each device
            "timestamp": datetime.now().isoformat(),  # Current timestamp
            "category": device_type  # Add category as a field
        })

    connection_metadata = get_connection_metadata()
    result = {
        "timestamp": datetime.now().isoformat(),
        "connection_metadata": connection_metadata,
        "devices": flattened_devices
    }

    # Send JSON structure to the webhook with retries
    for attempt in range(3):
        try:
            response = requests.post("https://ble-listener-286f94459e57.herokuapp.com/api/devices", json=result)
            print(f"Posted data to webhook, response status: {response.status_code}")
            break
        except ConnectionError as e:
            print(f"Connection error on attempt {attempt + 1}: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"An error occurred on attempt {attempt + 1}: {e}")
            time.sleep(5)

# Main function to run the scanning and listing every 5 seconds
def main():
    while True:
        asyncio.run(scan_and_list_devices())

if __name__ == "__main__":
    main()
