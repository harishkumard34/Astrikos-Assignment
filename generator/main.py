import time
import random
import json
import threading
from datetime import datetime, timezone
import requests

BACKEND_URL = "http://127.0.0.1:8000/ingest"

# Device configuration
DEVICES = [
    {"id": "pump-1", "type": "pump"},
    {"id": "pump-2", "type": "pump"},
    {"id": "cooling-unit-1", "type": "cooler"},
]

METRICS = {
    "pump": {
        "temperature": {"base": 70.0, "variance": 2.0},
        "vibration": {"base": 5.0, "variance": 0.5},
    },
    "cooler": {
        "temperature": {"base": 40.0, "variance": 1.5},
        "power_draw": {"base": 1500.0, "variance": 50.0},
    }
}

# State to simulate gradual failures
gradual_failures = {
    "pump-1": {"temperature": 0.0} # starts at 0 increase
}

def generate_reading(device_id, device_type, metric, config):
    base_val = config["base"]
    variance = config["variance"]
    
    # 1. Gradual Failure Logic (increase base over time)
    if device_id in gradual_failures and metric in gradual_failures[device_id]:
        # Increase temperature slowly to simulate gradual failure
        gradual_failures[device_id][metric] += 0.5 
        base_val += gradual_failures[device_id][metric]

    value = random.gauss(base_val, variance)

    # 2. Random Noise / Spike Logic (2% chance)
    if random.random() < 0.02:
        value += variance * 10 # Massive spike
        print(f"[SPIKE] Generated noisy spike for {device_id} {metric}")

    # 3. Sensor Fault Logic (1% chance)
    if random.random() < 0.01:
        value = 0.0
        print(f"[FAULT] Generated 0.0 fault for {device_id} {metric}")

    return {
        "device_id": device_id,
        "metric": metric,
        "value": round(value, 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def run_device(device):
    device_id = device["id"]
    device_type = device["type"]
    metrics_config = METRICS[device_type]

    while True:
        for metric, config in metrics_config.items():
            reading = generate_reading(device_id, device_type, metric, config)
            try:
                requests.post(BACKEND_URL, json=reading)
                print(f"Sent: {reading['device_id']} - {reading['metric']}: {reading['value']}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to send data (is backend running?): {e}")
                
        # Send data every 2 seconds
        time.sleep(2)

if __name__ == "__main__":
    print("Starting Data Generator...")
    threads = []
    for device in DEVICES:
        t = threading.Thread(target=run_device, args=(device,), daemon=True)
        t.start()
        threads.append(t)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping Data Generator.")
