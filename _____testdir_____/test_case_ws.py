import websocket
import json
import argparse
import time
from concurrent.futures import ThreadPoolExecutor

DEFAULT_WEBSOCKET_URL = "ws://13.201.132.202:3001"

# JSON object with arbitrary sensor data
sensor_data = {
    "device_id": "device123",
    "temperature": 20,
    "humidity": 50,
    "AB12cdEF": 45,
    "LMnopq34": 78,
    "uvWxyZ56": 12,
    "pqrS78XY": 90,
    "fgHiJK90": 67,
    "mnOPqr12": 34,
    "aBCdEF34": 88,
    "UVwxYZ89": 14,
    "qrstUV90": 23,
    "stUvWX56": 49,
    "XYzAbc78": 65,
    "CD23efGH": 19,
    "ijKlmN67": 33,
    "lmNopQ23": 57,
    "aBC45def": 80,
    "DE67ghIJ": 22,
    "gHjkL789": 95,
    "mnO56PQr": 41,
    "UVWX34yz": 31,
    "rsTuv567": 13,
    "tUVwXY23": 28,
    "zAbcDE78": 62,
    "EF56ghIJ": 79,
    "ijKlM123": 85,
    "LMnOpQ90": 54,
    "pqRsTU56": 71,
    "AbCD23ef": 47,
    "WXyZ45mn": 91,
    "Yz78abCD": 16,
    "cdEF67gh": 74,
    "iJKl89mn": 21,
    "opQR56st": 50,
    "uvWX90yz": 32,
    "xYZ23efG": 43,
    "hIJkL56m": 29,
    "NOqR78st": 66,
    "TUvwX23y": 55,
    "efGh45IJ": 87,
    "opQR56uv": 58,
    "wXYz78AB": 97,
    "noPQR67s": 25,
    "TUvWX34Y": 72,
    "GHiJ56kl": 37,
    "pqrS45UV": 48,
    "STuv89Wx": 86,
    "noPQ23ST": 39,
    "KLmN67op": 96,
    "rsUV45WX": 53
}

# Simulate a device sending data
def simulate_device(device_id, websocket_url):
    try:
        ws = websocket.WebSocket()
        ws.connect(websocket_url)
        print(f"Device {device_id}: Connected to WebSocket")

        # Update the device_id in the sensor_data for each device
        sensor_data["device_id"] = f"device_{device_id}"
        
        # Send the sensor data once
        ws.send(json.dumps(sensor_data))
        print(f"Device {device_id}: Sent data {sensor_data}")
        time.sleep(5)
        # Close the WebSocket connection
        # ws.close()
        # print(f"Device {device_id}: Connection closed after sending data")

    except Exception as e:
        print(f"Device {device_id}: Error occurred: {e}")

# Simulate multiple devices using 50 workers (threads)
def simulate_devices(num_of_devices, websocket_url):
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_of_devices) as executor:
        futures = [executor.submit(simulate_device, device_id, websocket_url) for device_id in range(1, num_of_devices + 1)]

        # Wait for all threads to complete
        for future in futures:
            future.result()

    end_time = time.time()
    print(f"All {num_of_devices} devices completed sending data points in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate multiple devices sending WebSocket messages.")
    
    parser.add_argument('--devices', type=int, default=50, help='Number of devices to simulate')
    parser.add_argument('--url', type=str, default=DEFAULT_WEBSOCKET_URL, help='WebSocket URL to connect to')

    args = parser.parse_args()

    print(f"Simulating {args.devices} devices, each sending WebSocket messages to {args.url}...")

    simulate_devices(args.devices, args.url)
