import requests
import random
from datetime import datetime

# --- CONFIG ---
# Make sure this matches your port (8000 or 8001)
API_URL = "http://localhost:8000/log_traffic"

# Defined Devices
PUMP_IP = "192.168.10.24"   # Infusion_Pump_A
BABY_IP = "192.168.10.15"   # Smart_Baby_Monitor

def send_anomaly(ip, device_name):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "src_ip": ip,
        "protocol": "TCP",
        "label": "Mirai-Attack",
        "flow_duration": 0.5,
        "tot_size": 5000,
        "rate": 1000,
        "srate": 500,
        "drate": 500,
        "iat": 0.01,
        "magnitude": 15.5,
        "radius": 2.5,
        "covariance": 5.0,
        "variance": 0.5,
        "weight": 5.0,
        "syn_count": 10,
        "ack_count": 0,
        "rst_count": 0,
        "fin_count": 0,
        "reconstruction_error": 0.99, # High Error
        "is_anomaly": True            # <--- FORCE TRUE
    }
    
    try:
        requests.post(API_URL, json=payload)
        print(f"✅ Sent FORCED ANOMALY for {device_name}")
    except Exception as e:
        print(f"❌ Error: {e}")

# --- EXECUTION ---
print("💥 Sending 5 anomalies for Infusion Pump...")
for _ in range(5):
    send_anomaly(PUMP_IP, "Infusion Pump")

print("💥 Sending 3 anomalies for Baby Monitor...")
for _ in range(3):
    send_anomaly(BABY_IP, "Baby Monitor")

print("DONE. Check Grafana now!")