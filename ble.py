import asyncio
from bleak import BleakScanner

# Manufacturer codes dictionary
manufacturer_codes = {
    0x004C: "Apple, Inc.",
    0x0006: "Microsoft",
    0x000F: "Broadcom Corporation",
    0x089A: "Teltonika",
    0xFD57: "Volvo"
    # Add more manufacturer codes as needed
}

# Function to categorize devices based on a pattern in their serial numbers
def categorize_device(name):
    if name and name.startswith("HRM"):  # Example pattern for Heart Rate Monitors
        return "Heart Rate Monitor"
    elif name and name.startswith("TMP"):  # Example pattern for Thermometers
        return "Thermometer"
    elif name and name.startswith("BPM"):  # Example pattern for Blood Pressure Monitors
        return "Blood Pressure Monitor"
    else:
        return "Unknown Device"

# Function to estimate distance from RSSI
def estimate_distance(rssi):
    tx_power = -59  # This is a common value, but it may vary
    if rssi == 0:
        return -1.0  # if we cannot determine accuracy, return -1.
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
        rssi = device.rssi
        distance = estimate_distance(rssi) if isinstance(rssi, int) else 'N/A'
        manufacturer_data = device.metadata.get('ManufacturerData', {})
        manufacturer_name = get_manufacturer_name(manufacturer_data)
        device_type = categorize_device(device.name)
        categorized_devices[device_type].append((device.name, device.address, rssi, distance, manufacturer_name))

    for category, devices in categorized_devices.items():
        print(f"{category}:")
        for name, address, rssi, distance, manufacturer_name in devices:
            distance_str = f"{distance:.2f} meters" if isinstance(distance, float) else distance
            print(f"  Name: {name}, Address: {address}, RSSI: {rssi}, Distance: {distance_str}, Manufacturer: {manufacturer_name}")
        print()

# Main function to run the scanning and listing
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scan_and_list_devices())
