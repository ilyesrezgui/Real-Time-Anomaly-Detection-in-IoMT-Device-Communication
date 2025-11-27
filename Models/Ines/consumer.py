import os
import json
import joblib
import numpy as np
from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import tensorflow as tf
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

print("RUNNING FROM:", os.getcwd())

# -------------------------
# Load LSTM model, scaler, threshold
# -------------------------
model = tf.keras.models.load_model(
    r"C:\Users\MSI\Videos\Downloads\Real-Time-Anomaly-Detection-in-IoMT-Device-Communication-1\Models\lstm_autoencoder.h5",
    custom_objects={"mse": tf.keras.losses.MeanSquaredError()}
)

scaler = joblib.load(
    r"C:\Users\MSI\Videos\Downloads\Real-Time-Anomaly-Detection-in-IoMT-Device-Communication-1\Models\scaler.pkl"
)

with open(r"C:\Users\MSI\Videos\Downloads\Real-Time-Anomaly-Detection-in-IoMT-Device-Communication-1\Models\numeric_features.json", "r") as f:
    numeric_features = json.load(f)

with open(r"C:\Users\MSI\Videos\Downloads\Real-Time-Anomaly-Detection-in-IoMT-Device-Communication-1\Models\threshold.json", "r") as f:
    threshold = float(json.load(f)["threshold"])

timesteps = len(numeric_features)
n_features = 1

# -------------------------
# Kafka Consumer
# -------------------------
consumer = KafkaConsumer(
    'iomt_traffic_stream',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest'
)
print("Kafka Consumer connected. Waiting for messages...")

# -------------------------
# InfluxDB Client
# -------------------------
influx_client = InfluxDBClient(
    url="http://localhost:8086",
    token="Wq6IQNlfN2D14Akf2Xo0dzHM8hLkVCg1Lxr4rBb0o7e3xE6PlRuJYdAw1ZQtpnhaygu0aVsW8Y9REw2q9KCuow==",
    org="OST"
)

write_api = influx_client.write_api(write_options=SYNCHRONOUS)
bucket = "iomt_data"

# -------------------------
# Feature list
# -------------------------
features = [
    "Header_Length", "Protocol Type", "Time_To_Live", "Rate",
    "fin_flag_number", "syn_flag_number", "psh_flag_number", "ack_flag_number",
    "ece_flag_number", "cwr_flag_number",
    "HTTP", "HTTPS", "DNS", "Telnet", "SMTP", "SSH", "IRC",
    "TCP", "UDP", "DHCP", "ARP", "ICMP", "IGMP",
    "Tot sum", "Min", "Max", "AVG", "Std", "IAT", "Number", "Variance"
]

# -------------------------
# Preprocess function
# -------------------------
def preprocess_message(data):
    row = [data.get(f, 0) for f in numeric_features]
    arr = np.array(row, dtype=np.float32).reshape(1, -1)
    arr = np.where(np.isfinite(arr), arr, 0)
    arr = np.clip(arr, -1e10, 1e10)
    arr_scaled = scaler.transform(arr)
    arr_scaled = arr_scaled.reshape(1, timesteps, n_features)
    return arr_scaled

# -------------------------
# Main Loop
# -------------------------
for msg in consumer:

    data = msg.value

    try:
        X = preprocess_message(data)
    except Exception as e:
        print("Skipping message due to error:", e, "Data:", data)
        continue

    reconstruction = model.predict(X, verbose=0)
    mae = np.mean(np.abs(reconstruction - X))
    is_anomaly = int(mae > threshold)

    try:
        point = Point("iomt_stream") \
            .field("mae", float(mae)) \
            .field("anomaly", is_anomaly)

        for f in features:
            if f in data:
                point = point.field(f.replace(" ", "_"), float(data[f]))

        write_api.write(bucket=bucket, record=point)
        print(f"MAE={mae:.6f} | threshold={threshold:.6f} | anomaly={is_anomaly}")


    except Exception as e:
        print("InfluxDB write error:", e)
