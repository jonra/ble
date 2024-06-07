import asyncio
from bleak import BleakScanner
import nest_asyncio

# Apply the nest_asyncio patch to allow nested event loops
nest_asyncio.apply()

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

async def scan_for_ble_devices(scan_duration=1, retries=3):
    devices = []
    for _ in range(retries):
        found_devices = await BleakScanner.discover(timeout=scan_duration)
        devices.extend(found_devices)
        # Use set to remove duplicates based on address
        devices = list({device.address: device for device in devices}.values())
        # If you have a specific device to look for, you can filter by its address
        # e.g., if target_device_address in [device.address for device in devices]:
        #     break

        # for device in devices:
        #     # print(device)
        #     if device.metadata.get(76):
        #         distance = estimate_distance(device.rssi)
        #         print(f"Device: {device.name or 'Unknown'}, Manufacturer: {device.metadata.get('manufacturer_data', {})}, Address: {device.address}, RSSI: {device.rssi}, Estimated Distance: {distance:.2f} meters")
        for device in devices:
            # print(f"Device: {device.name or 'Unknown'}, Manufacturer Data: {device.metadata.get('manufacturer_data', {})}, Address: {device.address}, RSSI: {device.rssi}")

            # Get the manufacturer data dictionary
            manufacturer_data = device.metadata.get('manufacturer_data', {})

            # Check if the manufacturer data contains key 76
            if 76 in manufacturer_data:
                distance = estimate_distance(device.rssi)
                print(f"Identified Device with key 76: {device.name or 'Unknown'}, Address: {device.address}, RSSI: {device.rssi}, Estimated Distance: {distance:.2f} meters")


def run_ble_scan(scan_duration=2, retries=3):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scan_for_ble_devices(scan_duration, retries))

if __name__ == "__main__":
    run_ble_scan()
