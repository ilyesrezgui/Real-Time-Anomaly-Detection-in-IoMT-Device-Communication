---

### Architecture Explanation

The system architecture is divided into **two main environments**:
**(1) Offline Training** and **(2) Real-Time Processing** — both integrated through a containerized Kubernetes deployment for scalability and automation.

---

#### **1. Offline Training Environment (Batch Layer)**

This part handles **model development and threshold calibration** before deployment.

* **Historical Normal Traffic (CICIoMT2023 Dataset):** Used to learn baseline IoMT communication behavior.
* **Data Preprocessing & Feature Engineering:** Extracts key traffic features like packet size, protocol type, duration, and flow statistics using Python (Pandas/Scapy).
* **LSTM Autoencoder Training:** The model learns normal traffic patterns in an unsupervised manner using TensorFlow/Keras.
* **Classifier Models (Random Forest / CNN):** Trained for evaluation and comparison to benchmark anomaly detection accuracy.
* **Model Registry (MLflow/DVC):** Stores trained models and metadata for versioning and reproducibility.
* **Threshold Optimization:** Determines the best anomaly threshold from reconstruction error distributions.

The trained and validated model (.h5) is then exported for use in the **real-time pipeline**.

---

#### **2. Real-Time Processing Pipeline (Streaming Layer)**

This layer continuously monitors IoMT traffic in real time to detect and respond to anomalies.

* **Kafka Producer/Broker:** Simulates and streams live IoMT network traffic.
* **Data Validation Layer:** Implements schema checks with Great Expectations to filter malformed or incomplete packets before processing.
* **Stream Processing (Spark/Flink):** Ingests, processes, and transforms incoming data streams.
* **Feature Extraction:** Uses Scapy and Pandas to extract relevant communication features from each network flow.
* **Anomaly Detection (LSTM Autoencoder):** Applies the pre-trained model to compute reconstruction errors and detect unusual behavior.
* **Anomaly Gate:** Compares anomaly scores against the optimized threshold to classify normal vs. abnormal communication.
* **Explainability Module (SHAP):** Provides interpretability by showing which features contributed most to each anomaly.

---

#### **3. Storage, Monitoring & Alerting Layer**

This layer ensures detected anomalies are stored, visualized, and acted upon.

* **InfluxDB:** Stores anomaly data and time-series metrics for analysis.
* **Grafana / Kibana Dashboards:** Visualize network traffic, device anomalies, and attack patterns in real time.
* **Alerting Service:** Sends notifications (email, Slack, etc.) when an anomaly is detected.
* **Containerization (Docker + Kubernetes):** Ensures modularity, scalability, and secure deployment across multiple nodes.
* **Security Layer (TLS, RBAC):** Protects data and service communication, ensuring compliance with healthcare network standards.

---

### In Summary

* **Offline layer** builds and tunes models.
* **Real-time layer** streams IoMT traffic and applies those models.
* **Monitoring layer** stores, visualizes, and alerts on anomalies.
* All components run in **containerized services within a secure Kubernetes cluster**, making the system scalable and production-ready for healthcare environments.

---

