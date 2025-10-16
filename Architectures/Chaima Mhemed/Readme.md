<!-- Architecture Explanation Section -->


## Overview

This project aims to design a real-time anomaly detection system for the Internet of Medical Things (IoMT). The system monitors device-to-device communication (e.g., patient monitors, infusion pumps, wearables) to identify unusual or malicious behavior in real-time.

By analyzing network traffic from the CICIoMT2023 dataset, the system detects anomalies, triggers alerts, and visualizes key metrics to help healthcare operators respond to cyber threats or device malfunctions efficiently.



---

## Proposed Architecture

### Components Description

1. Data Source — CICIoMT2023 Dataset

- Provides IoMT network traffic data containing both normal and attack scenarios.

- Simulates real-world medical device communications for testing anomaly detection algorithms.

2. Kafka (Producer & Consumer)

- Kafka Producer: Streams simulated IoMT traffic from the CICIoMT2023 dataset in real time.

- Kafka Consumer: Works with Apache Spark to consume data streams for preprocessing and analysis.

3. Apache Spark + Python

- Performs real-time preprocessing and feature extraction (e.g., packet size, duration, flow count, protocol type).

- Extracted features are then passed to the anomaly detection model.

4. Autoencoders (LSTM/Deep Autoencoders)

- Learn the normal communication behavior of IoMT devices in an unsupervised way.

- Compute reconstruction errors to identify potential anomalies.

5. Random Forest / Isolation Forest

- Serve as secondary classifiers to evaluate or validate the detected anomalies in batch mode.

- Help distinguish between benign and malicious traffic more robustly.

6. InfluxDB

- Stores anomaly scores, device metrics, and alert logs for further analysis.

- Supports both real-time and historical data queries.

7. Grafana

- Visualizes real-time monitoring dashboards showing:

-> Anomaly frequency over time

-> Device health and status

-> Attack patterns per device type

- Facilitates quick anomaly investigation by healthcare operators.

8. Docker (and optionally Kubernetes)

- Each component (Kafka, Spark, InfluxDB, Grafana) is containerized using Docker.

- Enables scalable deployment and easy orchestration across distributed environments.


---

### Data Processing Pipelines

### Pipeline 1: IoMT Traffic Simulation

- Kafka simulates IoMT device traffic using the CICIoMT2023 dataset.

### Pipeline 2: Preprocessing & Feature Extraction

- Spark + Python clean and transform streaming data.

- Extract features like:

Packet size

Duration

Flow count

Protocol type

Source/destination IPs

### Pipeline 3: Anomaly Detection

- LSTM Autoencoder computes reconstruction error for each traffic flow.

- Higher reconstruction error → higher probability of anomaly.

### Pipeline 4: Alerting & Storage

- Detected anomalies are stored in InfluxDB with timestamped metadata.

- Alerts can be sent via email, Slack, or other configured channels.

### Pipeline 5: Visualization

- Grafana dashboards display:

Real-time anomaly trends

Communication metrics

Device behavior summaries
