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



