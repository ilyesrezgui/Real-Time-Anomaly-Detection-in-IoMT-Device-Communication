import requests
import random
import time
from datetime import datetime

# This is where your API is living
API_URL = "http://localhost:8000/log_traffic"

# Fake devices to simulate
DEVICES = [
    "192.168.10.14", # Smart Thermostat
    "192.168.10.15", # Baby Monitor
    "192.168.10.24", # Infusion Pump (We will make this one fail!)
]

print("🚑 Starting Medical Device Simulation... (Press Ctrl+C to stop)")

for i in range(10): # We will send 10 data points
    
    # Pick a random device
    ip = random.choice(DEVICES)
    
    # Simulate an anomaly: If it's the Infusion Pump, make it look bad
    is_pump = (ip == "192.168.10.24")
    rec_error = random.uniform(0.5, 1.0) if is_pump else random.uniform(0.001, 0.05)
    is_anomaly = True if is_pump else False

    # The payload matching your API schema
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "src_ip": ip,
        "protocol": "TCP",
        "label": "DDoS-ICMP_Flood" if is_pump else "Benign",
        "flow_duration": random.uniform(0.1, 5.0),
        "tot_size": random.randint(100, 5000),
        "rate": random.uniform(10, 1000),
        "srate": random.uniform(10, 1000),
        "drate": random.uniform(10, 1000),
        "iat": random.uniform(0.0, 0.1),
        "magnitude": random.uniform(5, 20),
        "radius": random.uniform(1, 5),
        "covariance": random.uniform(1, 10),
        "variance": random.uniform(0.1, 1.0),
        "weight": random.uniform(1, 10),
        "syn_count": 0,
        "ack_count": 5,
        "rst_count": 0,
        "fin_count": 1,
        "reconstruction_error": rec_error,
        "is_anomaly": is_anomaly
    }

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print(f"✅ Sent data for {ip} -> Type: {response.json().get('device')}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: Is your API running? {e}")

    time.sleep(1)

print("Done! Now check your Grafana or run the Export script again.")