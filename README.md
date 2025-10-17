Topic 6: Real-Time Anomaly Detection in IoMT Device Communication (IoMT-AD)
Description:
This project will build a system to analyze and detect abnormal behavior on the Internet of Medical Things (IoMT) devices such as patient monitors, infusion pumps, and wearables. The focus is on identifying unusual communication patterns that may indicate device malfunctions or cyberattacks. By analyzing real-time traffic streams, the system will flag anomalies, trigger alerts, and provide visualization dashboards to help healthcare operators respond quickly.
Team Size: 5
Mentored by: Loubna Seddiki (seddikiloubna@inf.elte.hu)
Dataset:
CICIoMT2023 Dataset (IoMT network traffic with both normal and attack scenarios)
Open-Source Technologies to be Used:
Data Simulation & Ingestion: Use Kafka to simulate and ingest IoMT traffic from CICIoMT2023 in real time.
Preprocessing & Feature Engineering: Extract communication features such as packet size, protocol type, connection duration, and flow statistics using Python (Pandas, Scapy).
Anomaly Detection Model: Train LSTM autoencoders for unsupervised anomaly detection and use TensorFlow/Keras for model training and inference.
Stream Processing: Use Apache Spark Streaming or Flink to process traffic flows, apply feature extraction, and run real-time inference.
Visualization & Alerts: Implement dashboards with Grafana or Kibana to monitor device traffic, anomaly scores, and attack patterns. Integrate alerting mechanisms (email, Slack, SMS).
Storage: Use InfluxDB to store IoMT traffic metrics, anomalies, and alerts for later analysis.
Deployment & Containerization: Package system components with Docker and orchestrate them with Kubernetes for scalability in healthcare network environments.
Batch Processing Tasks:
Train an LSTM autoencoder model on historical normal IoMT traffic to learn baseline device communication behavior.
Train classification models (e.g., Random Forest, CNN) to distinguish between normal and malicious traffic for evaluation.
Tune thresholds for anomaly detection based on reconstruction error distributions.
Real-Time Processing Pipelines:
Pipeline 1: Simulating IoMT Traffic. Replay CICIoMT2023 traffic streams using Kafka to emulate real-world IoMT communication.
Pipeline 2: Data Preprocessing & Feature Extraction. Extract relevant network features (packet size, duration, flow count, protocols) and normalize them in real time.
Pipeline 3: Anomaly Detection Model. Apply the LSTM autoencoder to incoming traffic and compute reconstruction error to flag unusual device communication.
Pipeline 4: Alerting & Forensic Storage. Generate alerts for abnormal behavior, store flagged sessions in InfluxDB, and mark them for forensic investigation.
Pipeline 5: Visualization & Monitoring. Use Grafana/Kibana dashboards to show device health, anomaly frequency over time, and heatmaps of attack patterns per device type.
