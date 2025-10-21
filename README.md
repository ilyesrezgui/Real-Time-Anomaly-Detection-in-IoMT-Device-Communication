# 🩺 IoMT-AD: Real-Time Anomaly Detection in IoMT Device Communication

## 📘 Description
**IoMT-AD** (Internet of Medical Things - Anomaly Detection) is a system designed to **analyze and detect abnormal behavior** in IoMT devices such as patient monitors, infusion pumps, and wearables.  
It identifies unusual communication patterns that may indicate **device malfunctions** or **cyberattacks** by analyzing real-time traffic streams.

The system **flags anomalies**, **triggers alerts**, and provides **visual dashboards** to help healthcare operators respond quickly.

---

## 👥 Team Information
- **Team Size:** 5  
- **Mentored by:** *Loubna Seddiki*  
- **Email:** [seddikiloubna@inf.elte.hu](mailto:seddikiloubna@inf.elte.hu)

---

## 📊 Dataset
- **Dataset Used:** [CICIoMT2023](https://www.unb.ca/cic/datasets/iomt.html)  
  *(IoMT network traffic dataset with both normal and attack scenarios)*

---

## 🧠 System Architecture Overview

### 🔹 Components
1. **Data Simulation & Ingestion**
   - Simulate IoMT traffic using **Kafka** (Producer–Consumer architecture)
   - Replay CICIoMT2023 data in real time

2. **Preprocessing & Feature Engineering**
   - Use **Python (Pandas, Scapy)** to extract:
     - Packet size  
     - Protocol type  
     - Connection duration  
     - Flow statistics

3. **Anomaly Detection Model**
   - Train **LSTM Autoencoders** (unsupervised)
   - Frameworks: **TensorFlow/Keras**
   - Detect anomalies using **reconstruction error thresholds**

4. **Stream Processing**
   - Real-time flow processing using **Apache Spark Streaming** or **Apache Flink**
   - Apply transformations and inference pipelines on live data

5. **Visualization & Alerts**
   - **Grafana** or **Kibana** dashboards for:
     - Device traffic monitoring  
     - Anomaly scores  
     - Attack pattern heatmaps  
   - Alerting via **Email, Slack, SMS**

6. **Storage**
   - **InfluxDB** for:
     - IoMT traffic metrics  
     - Detected anomalies  
     - Alerts and forensic data

7. **Deployment & Containerization**
   - **Docker** for containerization  
   - **Kubernetes** for orchestration and scalability

---

## ⚙️ Batch Processing Tasks
- Train **LSTM Autoencoder** on historical *normal* IoMT traffic.
- Train **classification models** (Random Forest, CNN) for evaluation.
- Tune **detection thresholds** based on reconstruction error distributions.

---

## 🔄 Real-Time Processing Pipelines

### 🧩 Pipeline 1: Simulating IoMT Traffic
- Replay CICIoMT2023 traffic using **Kafka Producer**.
- Emulate real-world IoMT device communication.

### ⚙️ Pipeline 2: Data Preprocessing & Feature Extraction
- Extract features in real time:
  - Packet size, duration, flow count, protocols
- Normalize data streams before feeding them into the model.

### 🧠 Pipeline 3: Anomaly Detection Model
- Apply the **LSTM Autoencoder** to streaming data.
- Compute **reconstruction error**.
- Flag unusual or suspicious device behavior.

### 🚨 Pipeline 4: Alerting & Forensic Storage
- Generate alerts for abnormal communication.
- Store flagged sessions in **InfluxDB** for forensic analysis.

### 📊 Pipeline 5: Visualization & Monitoring
- Use **Grafana/Kibana** dashboards to visualize:
  - Device health status  
  - Anomaly frequency over time  
  - Attack patterns by device type

---

## 🧰 Open-Source Technologies Used

| Component | Technology |
|------------|-------------|
| **Data Simulation** | Apache Kafka |
| **Processing** | Apache Spark Streaming / Flink |
| **Modeling** | TensorFlow / Keras |
| **Preprocessing** | Pandas, Scapy |
| **Storage** | InfluxDB |
| **Visualization** | Grafana / Kibana |
| **Containerization** | Docker, Kubernetes |

---

## 🚀 Deployment
```bash
# Clone the repository
git clone https://github.com/yourusername/IoMT-AD.git
cd IoMT-AD

# Build Docker containers
docker-compose build

# Run the full system
docker-compose up
