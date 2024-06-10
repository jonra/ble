import asyncio
from bleak import BleakScanner

# Function to categorize devices based on a pattern in their serial numbers
def categorize_device(name):
    if name.startswith("HRM"):  # Example pattern for Heart Rate Monitors
        return "Heart Rate Monitor"
    elif name.startswith("TMP"):  # Example pattern for Thermometers
        return "Thermometer"
    elif name.startswith("BPM"):  # Example pattern for Blood Pressure Monitors
        return "Blood Pressure Monitor"
    else:
        return "Unknown Device"

# Function to scan for devices and list them grouped by type
async def scan_and_list_devices():
    devices = await BleakScanner.discover()
    categorized_devices = {
        "Heart Rate Monitor": [],
        "Thermometer": [],
        "Blood Pressure Monitor": [],
        "Unknown Device": []
    }

    for device in devices:
        rssi = device.metadata.get('rssi', 'N/A')
        device_type = categorize_device(device.name)
        categorized_devices[device_type].append((device.name, device.address, rssi))

    for category, devices in categorized_devices.items():
        print(f"{category}:")
        for name, address, rssi in devices:
            print(f"  Name: {name}, Address: {address}, RSSI: {rssi}")
        print()

# Main function to run the scanning and listing
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scan_and_list_devices())
