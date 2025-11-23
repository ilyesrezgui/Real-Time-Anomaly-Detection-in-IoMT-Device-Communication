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
    threshold = json.load(f)["threshold"]

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

