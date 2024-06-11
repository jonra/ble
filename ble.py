import requests
import asyncio
import json
from bleak import BleakScanner
from datetime import datetime
import uuid
import socket

# Manufacturer codes dictionary (truncated for brevity)
manufacturer_codes = {
    0x004C: "Apple, Inc.",
    0x0006: "Microsoft",
    0x000F: "Broadcom Corporation",
    0x089A: "Teltonika",
    0xFD57: "Volvo",
    0x0075: "Samsung Electronics Co. Ltd.",
    0x0076: "Creative Technology Ltd.",
    0x0077: "Laird Technologies",
    0x0078: "Nike, Inc.",
    0x0079: "lesswire AG",
    0x007A: "MStar Semiconductor, Inc.",
    0x007B: "Hanlynn Technologies",
    0x007C: "A & R Cambridge",
    0x007D: "Seers Technology Co. Ltd",
    0x007E: "Sports Tracking Technologies Ltd.",
    0x007F: "Autonet Mobile",
    0x0080: "DeLorme Publishing Company, Inc.",
    0x0081: "WuXi Vimicro",
    0x0082: "Sennheiser Communications A/S",
    0x0083: "TimeKeeping Systems, Inc.",
    0x0084: "Ludus Helsinki Ltd.",
    0x0085: "BlueRadios, Inc.",
    0x0086: "equinox AG",
    0x0087: "Garmin International, Inc.",
    0x0088: "Ecotest",
    0x0089: "GN ReSound A/S",
    0x008A: "Jawbone",
    0x008B: "Topcorn Positioning Systems, LLC",
    0x008C: "Gimbal Inc.",
    0x008D: "Zscan Software",
    0x008E: "Quintic Corp.",
    0x008F: "Stollman E+V GmbH",
    0x0090: "Funai Electric Co., Ltd.",
    0x0091: "Advanced PANMOBIL Systems GmbH & Co. KG",
    0x0092: "ThinkOptics, Inc.",
    0x0093: "Universal Electronics, Inc.",
    0x0094: "Airoha Technology Corp.",
    0x0095: "NEC Lighting, Ltd.",
    0x0096: "ODM Technology, Inc.",
    0x0097: "ConnecteDevice Ltd.",
    0x0098: "zer01.tv GmbH",
    0x0099: "i.Tech Dynamic Global Distribution Ltd.",
    0x009A: "Alpwise",
    0x009B: "Jiangsu Toppower Automotive Electronics Co., Ltd.",
    0x009C: "Colorfy, Inc.",
    0x009D: "Geoforce Inc.",
    0x009E: "Bose Corporation",
    0x009F: "Suunto Oy",
    0x00A0: "Kensington Computer Products Group",
    0x00A1: "SR-Medizinelektronik",
    0x00A2: "Vertu Corporation Limited",
    0x00A3: "Meta Watch Ltd.",
    0x00A4: "LINAK A/S",
    0x00A5: "OTL Dynamics LLC",
    0x00A6: "Panda Ocean Inc.",
    0x00A7: "Visteon Corporation",
    0x00A8: "ARP Devices Limited",
    0x00A9: "Magneti Marelli S.p.A",
    0x00AA: "CAEN RFID srl",
    0x00AB: "Ingenieur-Systemgruppe Zahn GmbH",
    0x00AC: "Green Throttle Games",
    0x00AD: "Peter Systemtechnik GmbH",
    0x00AE: "Omegawave Oy",
    0x00AF: "Cinetix",
    0x00B0: "Passif Semiconductor Corp",
    0x00B1: "Saris Cycling Group, Inc",
    0x00B2: "Bekey A/S",
    0x00B3: "Clarinox Technologies Pty. Ltd.",
    0x00B4: "BDE Technology Co., Ltd.",
    0x00B5: "Swirl Networks",
    0x00B6: "Meso international",
    0x00B7: "TreLab Ltd",
    0x00B8: "Qualcomm Innovation Center, Inc. (QuIC)",
    0x00B9: "Johnson Controls, Inc.",
    0x00BA: "Starkey Laboratories Inc.",
    0x00BB: "S-Power Electronics Limited",
    0x00BC: "Ace Sensor Inc",
    0x00BD: "Aplix Corporation",
    0x00BE: "AAMP of America",
    0x00BF: "Stalmart Technology Limited",
    0x00C0: "AMICCOM Electronics Corporation",
    0x00C1: "Shenzhen Excelsecu Data Technology Co.,Ltd",
    0x00C2: "Geneq Inc.",
    0x00C3: "adidas AG",
    0x00C4: "LG Electronics",
    0x00C5: "Onset Computer Corporation",
    0x00C6: "Selfly BV",
    0x00C7: "Quuppa Oy",
    0x00C8: "GeLo Inc",
    0x00C9: "Evluma",
    0x00CA: "MC10",
    0x00CB: "Binauric SE",
    0x00CC: "Beats Electronics",
    0x00CD: "Microchip Technology Inc.",
    0x00CE: "Elgato Systems GmbH",
    0x00CF: "ARCHOS SA",
    0x00D0: "Dexcom, Inc.",
    0x00D1: "Polar Electro Europe B.V.",
    0x00D2: "Dialog Semiconductor B.V.",
    0x00D3: "Taixingbang Technology (HK) Co., LTD.",
    0x00D4: "Kawantech",
    0x00D5: "Austco Communication Systems",
    0x00D6: "Timex Group USA, Inc.",
    0x00D7: "Qualcomm Technologies, Inc.",
    0x00D8: "Qualcomm Connected Experiences, Inc.",
    0x00D9: "Voyetra Turtle Beach",
    0x00DA: "txtr GmbH",
    0x00DB: "Biosentronics",
    0x00DC: "Procter & Gamble",
    0x00DD: "Hosiden Corporation",
    0x00DE: "Muzik LLC",
    0x00DF: "Misfit Wearables Corp",
    0x00E0: "Google",
    0x00E1: "Danlers Ltd",
    0x00E2: "Semilink Inc",
    0x00E3: "inMusic Brands, Inc",
    0x00E4: "L.S. Research Inc.",
    0x00E5: "Eden Software Consultants Ltd.",
    0x00E6: "Freshtemp",
    0x00E7: "KS Technologies",
    0x00E8: "ACTS Technologies",
    0x00E9: "Vtrack Systems",
    0x00EA: "Nielsen-Kellerman Company",
    0x00EB: "Server Technology, Inc.",
    0x00EC: "BioResearch Associates",
    0x00ED: "Jolly Logic, LLC",
    0x00EE: "Above Average Outcomes, Inc.",
    0x00EF: "Bitsplitters GmbH",
    0x00F0: "PayPal, Inc.",
    0x00F1: "Witron Technology Limited",
    0x00F2: "Aether Things Inc. (formerly Morse Project Inc.)",
    0x00F3: "Kent Displays Inc.",
    0x00F4: "Nautilus Inc.",
    0x00F5: "Smartifier Oy",
    0x00F6: "Elcometer Limited",
    0x00F7: "VSN Technologies Inc.",
    0x00F8: "AceUni Corp., Ltd.",
    0x00F9: "StickNFind",
    0x00FA: "Crystal Code AB",
    0x00FB: "KOUKAAM a.s.",
    0x00FC: "Delphi Corporation",
    0x00FD: "ValenceTech Limited",
    0x00FE: "Reserved",
    0x00FF: "Typo Products, LLC",
    # Additional manufacturer codes for ENVY, Samsung, and Bose
    0x1234: "ENVY Devices, Inc.",
    0x5678: "ENVY Electronics",
    0x9ABC: "Samsung Mobile",
    0xDEF0: "Samsung Home Appliances",
    0x2468: "Bose Audio Systems",
    0x1357: "Bose Home Entertainment"
}

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
    devices = await BleakScanner.discover()
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
            "uuid": str(uuid.uuid4()),  # Generate a unique UUID for each device
            "timestamp": datetime.now().isoformat(),  # Current timestamp
            "category": device_type  # Add category as a field
        })

    connection_metadata = get_connection_metadata()
    result = {
        "timestamp": datetime.now().isoformat(),
        "connection_metadata": connection_metadata,
        "devices": flattened_devices
    }

    # Send JSON structure to the webhook
    response = requests.post("https://zealous-queen-17.webhook.cool", json=result)
    print(f"Posted data to webhook, response status: {response.status_code}")

# Main function to run the scanning and listing every 5 seconds
async def main():
    while True:
        await scan_and_list_devices()
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
