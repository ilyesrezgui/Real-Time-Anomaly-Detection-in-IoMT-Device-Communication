# Iness
# IoMT Real-Time Anomaly Detection System  
LSTM Autoencoder + Kafka + InfluxDB + Grafana + Docker

---

## 🚀 Project Overview

This project implements a **real-time anomaly detection pipeline** for IoMT (Internet of Medical Things) network traffic.  
It uses a trained **LSTM Autoencoder** model to detect abnormal communication patterns and visualizes them through Grafana.

The system components:

- **Model:** LSTM Autoencoder (Python + TensorFlow) Models\Iness\model.ipynb
- **Real-time Processing:** Kafka Consumer          Models\Iness\consumer.py
- **Database:** InfluxDB (time-series)              Models\Iness\consumer.py
- **Dashboard:** Grafana                            Models\Iness\Grafana.json
- **Deployment:** Docker & Docker Compose           apps\Dockerfile.consumer

---

# 📡 System Architecture




---

# 🧠 Model (Training Script)

The model is trained using the script:

➡ `model.ipynb`

### ✔ Training Steps

1. Load dataset  
2. Select numeric features  
3. Drop highly correlated features  
4. Split data (train, validation, test)  
5. Scale data with MinMaxScaler  
6. Train LSTM Autoencoder  
7. Compute threshold (99th percentile MAE)  
8. Save output files:
lstm_autoencoder.h5,
scaler.pkl,
numeric_features.json,
threshold.json


This model is used by the Kafka consumer for real-time anomaly detection.

---

# 🔍 Kafka Anomaly Consumer

File: **`consumer.py`**

The consumer:

- Loads the trained model + scaler + numeric features
- Connects to Kafka topic: `iomt_traffic_stream`
- Preprocesses each incoming message
- Computes MAE reconstruction error
- Flags anomaly if: MAE > threshold

- Stores results in InfluxDB (measurement: `iomt_stream`)





