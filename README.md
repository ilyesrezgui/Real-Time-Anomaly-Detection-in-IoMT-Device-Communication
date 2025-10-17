# Real-Time Anomaly Detection in IoMT Device Communication (IoMT-AD)

**Team Size:** 5  
**Mentor:** Loubna Seddiki (seddikiloubna@inf.elte.hu)  

---

## Project Overview

The **IoMT-AD** project aims to detect abnormal behavior in Internet of Medical Things (IoMT) devices, such as patient monitors, infusion pumps, and wearables, in **real-time**. By analyzing network traffic, the system can flag unusual communication patterns that may indicate device malfunctions or cyberattacks, helping healthcare operators respond promptly.  

---

## Key Features

- Real-time detection of anomalies in IoMT network traffic.
- Visualization dashboards for monitoring device health and attack patterns.
- Alerting mechanisms (email, Slack, SMS) for quick response.
- Scalable deployment using containerization and orchestration (Docker & Kubernetes).

---

## Dataset

**CICIoMT2023 Dataset**  
- Contains IoMT network traffic for both normal operations and attack scenarios.  
- Used for both model training and real-time simulation.

---

## Architecture & Pipelines

### Batch Processing
1. **Model Training:**  
   - Train **LSTM Autoencoders** on normal IoMT traffic to learn baseline behavior.  
   - Train classification models (Random Forest, CNN) to evaluate normal vs malicious traffic.  
2. **Threshold Tuning:**  
   - Determine anomaly detection thresholds based on reconstruction error distributions.

### Real-Time Processing Pipelines
1. **Simulating IoMT Traffic:**  
   - Replay CICIoMT2023 traffic streams using **Kafka** to emulate real-world IoMT communication.
2. **Data Preprocessing & Feature Extraction:**  
   - Extract features like packet size, protocol type, connection duration, and flow statistics using **Python (Pandas, Scapy)**.  
   - Normalize and prepare features in real-time.  
3. **Anomaly Detection:**  
   - Apply **LSTM Autoencoder** for reconstruction error-based anomaly detection.  
   - Flag unusual device communication.  
4. **Alerting & Forensic Storage:**  
   - Generate alerts for abnormal behavior.  
   - Store flagged sessions in **InfluxDB** for forensic investigation.  
5. **Visualization & Monitoring:**  
   - Use **Grafana/Kibana** dashboards to track device health, anomaly frequency, and attack patterns.  



