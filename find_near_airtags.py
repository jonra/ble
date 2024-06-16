import asyncio
from bleak import BleakScanner
import nest_asyncio

# Apply the nest_asyncio patch to allow nested event loops
nest_asyncio.apply()

manufacturer_codes = {
    0x004C: "Apple, Inc.",
    0x089A: "Teltonika",
    0x0105: "Ubiquitous Computing Technology Corporation", # iTag
    0x0065: "HP, Inc.",
    0x03FE: "Littelfuse" # Lynk&Co
    # Add more manufacturer codes as needed
}

def estimate_distance(rssi, tx_power=-59, n=2):
    """
    Estimate the distance to a BLE device based on the RSSI value.
    Args:
    - rssi: The RSSI value
    - tx_power: The TxPower value at 1 meter (default is -59 dBm)
    - n: The path-loss exponent (default is 2, typical for free space)
    Returns:
    - Estimated distance in meters
    """
    return 10 ** ((tx_power - rssi) / (10 * n))

async def scan_for_ble_devices(scan_duration=1, retries=1):
    devices = []
    for _ in range(retries):
        found_devices = await BleakScanner.discover(timeout=scan_duration)
        devices.extend(found_devices)
        # Use set to remove duplicates based on address
        devices = list({device.address: device for device in devices}.values())

    for device in devices:
        distance = estimate_distance(device.rssi)
        manufacturer_data = device.metadata.get('manufacturer_data', {})
        # print(manufacturer_data)
        
        for key, value in manufacturer_data.items():
            # Find  manufacturer name
            manufacturer_name = manufacturer_codes.get(key, f"Unknown ({key})")
            # Skip Apple devices
            if manufacturer_name.startswith("Apple"):
                continue
            # Identify manufacter identifier
            manufacturer_identifier = key
            manufacturer_identifier_hex = f"{manufacturer_identifier:04X}"  # Convert to hexadecimal format


            if manufacturer_name.startswith("Unknown"):
                print(f"Unknown Manufacturer Code: {key}, Data: {value}")
            # Print information
            print(f"Device: {device.name or 'Unknown'}, Manufacturer: {manufacturer_name}, Manufactorer Identifier: 0x{manufacturer_identifier_hex}, Address: {device.address}, RSSI: {device.rssi}, Estimated Distance: {distance:.2f} meters")

def run_ble_scan(scan_duration=2, retries=3):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scan_for_ble_devices(scan_duration, retries))

if __name__ == "__main__":
    run_ble_scan()
