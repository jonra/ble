import asyncio
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError

# Function to explore services and characteristics of a device
async def explore_device(address):
    try:
        async with BleakClient(address) as client:
            await client.connect()
            services = client.services
            for service in services:
                print(f"Service: {service.uuid}, Description: {service.description}")
                for char in service.characteristics:
                    print(f"  Characteristic: {char.uuid}, Properties: {char.properties}")
    except BleakError as e:
        print(f"Failed to connect to device at {address}: {e}")

# Function to identify if a device is a Heart Rate Monitor
async def identify_heart_rate_monitor(address):
    try:
        async with BleakClient(address) as client:
            await client.connect()
            services = client.services
            for service in services:
                if service.uuid == "0000180d-0000-1000-8000-00805f9b34fb":
                    print(f"Heart Rate Monitor identified at address: {address}")
                    return True
        return False
    except BleakError as e:
        print(f"Failed to connect to device at {address}: {e}")
        return False

# Function to scan for devices and identify their types
async def scan_and_identify():
    devices = await BleakScanner.discover()
    for device in devices:
        rssi = device.metadata.get('rssi', 'N/A')
        print(f"Scanning {device.name}, Address: {device.address}, RSSI: {rssi}")
        if await identify_heart_rate_monitor(device.address):
            continue
        else:
            await explore_device(device.address)

# Main function to run the scanning and identification
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scan_and_identify())
