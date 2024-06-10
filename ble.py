import asyncio
from bleak import BleakScanner, BleakClient

# Function to explore services and characteristics of a device
async def explore_device(address):
    async with BleakClient(address) as client:
        services = await client.get_services()
        for service in services:
            print(f"Service: {service.uuid}, Description: {service.description}")
            for char in service.characteristics:
                print(f"  Characteristic: {char.uuid}, Properties: {char.properties}")
                for descriptor in char.descriptors:
                    print(f"    Descriptor: {descriptor.uuid}, Value: {await client.read_gatt_descriptor(descriptor.handle)}")

# Function to identify if a device is a Heart Rate Monitor
async def identify_heart_rate_monitor(address):
    async with BleakClient(address) as client:
        services = await client.get_services()
        for service in services:
            if service.uuid == "0000180d-0000-1000-8000-00805f9b34fb":
                print("Heart Rate Monitor found!")
                return True
        return False

# Function to scan for devices and identify their types
async def scan_and_identify():
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Scanning {device.name}, Address: {device.address}, RSSI: {device.rssi}")
        if await identify_heart_rate_monitor(device.address):
            print(f"Heart Rate Monitor identified: {device.name}, Address: {device.address}")
        else:
            await explore_device(device.address)

# Main function to run the scanning and identification
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scan_and_identify())
