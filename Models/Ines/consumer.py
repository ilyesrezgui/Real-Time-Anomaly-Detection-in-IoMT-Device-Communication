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
# Load configuration from environment variables
# -------------------------
MODEL_PATH = os.getenv("MODEL_PATH", "/app/Models/Ines/lstm_autoencoder.h5")
SCALER_PATH = os.getenv("SCALER_PATH", "/app/Models/Ines/scaler.pkl")
NUMERIC_FEATURES_PATH = os.getenv("NUMERIC_FEATURES_PATH", "/app/Models/Ines/numeric_features.json")
THRESHOLD_PATH = os.getenv("THRESHOLD_PATH", "/app/Models/Ines/threshold.json")

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "iomt_traffic_stream")

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "OST")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "iomt_data")

# -------------------------
# Load Model + Files
# -------------------------
model = tf.keras.models.load_model(
    MODEL_PATH,
    custom_objects={"mse": tf.keras.losses.MeanSquaredError()}
)

scaler = joblib.load(SCALER_PATH)

with open(NUMERIC_FEATURES_PATH, "r") as f:
    numeric_features = json.load(f)

with open(THRESHOLD_PATH, "r") as f:
    threshold = float(json.load(f)["threshold"])

timesteps = len(numeric_features)
n_features = 1

# -------------------------
# Kafka Consumer
# -------------------------
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest'
)
print(f"Kafka Consumer connected → {KAFKA_BROKER} | topic={KAFKA_TOPIC}")

# -------------------------
# InfluxDB Client
# -------------------------
influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# -------------------------
# Preprocess
# -------------------------
def preprocess_message(data):
    row = [data.get(f, 0) for f in numeric_features]
    arr = np.array(row, dtype=np.float32).reshape(1, -1)
    arr = np.where(np.isfinite(arr), arr, 0)
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
        print("Preprocessing error, skipping:", e)
        continue

    reconstruction = model.predict(X, verbose=0)
    mae = np.mean(np.abs(reconstruction - X))
    is_anomaly = int(mae > threshold)

    try:
        point = Point("iomt_stream") \
            .field("mae", float(mae)) \
            .field("anomaly", is_anomaly)

        for k, v in data.items():
            if isinstance(v, (int, float)):
                point = point.field(k.replace(" ", "_"), float(v))

        write_api.write(bucket=INFLUXDB_BUCKET, record=point)

        print(f"MAE={mae:.6f} | TH={threshold:.6f} | anomaly={is_anomaly}")

    except Exception as e:
        print("InfluxDB error:", e)
