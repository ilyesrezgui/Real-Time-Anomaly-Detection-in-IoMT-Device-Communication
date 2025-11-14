# 🏥 IoMT Forensic Storage & Visualization Layer

This module implements the **Forensic Storage Layer** for the IoMT Anomaly Detection pipeline. It is responsible for ingesting processed network traffic (based on the **CICIoT2023** dataset), storing it in a time-series database, identifying failing medical devices, and exporting data for model retraining.

## 🌟 Features

  * **High-Throughput Ingestion:** FastAPI endpoint to receive real-time traffic logs.
  * **Time-Series Storage:** InfluxDB container for efficient storage of high-volume network flows.
  * **Device Mapping:** Automatically maps IP addresses to specific Medical Device types (e.g., Infusion Pumps, MRI Scanners).
  * **Forensic Visualization:** Grafana dashboard to identify "Top Failing Devices" and anomaly trends.
  * **ML Pipeline Integration:** Automated CSV export script for batch model retraining.

## 📂 Project Structure

  * `api.py`: The main ingestion server (FastAPI). Matches CICIoT2023 schema.
  * `simulate_traffic.py`: Script to generate synthetic traffic and anomalies for testing.
  * `export_data.py`: Extracts historical data to CSV for the ML team.
  * `force_anomalies.py`: Helper script to demonstrate specific attack scenarios.
  * `requirements.txt`: Python dependencies.

## 🚀 Setup & Installation

### 1\. Start the Infrastructure

This project requires **Docker**. Run the following commands to start the Database and Dashboard:

```bash
# 1. Start InfluxDB (The Database)
docker run -d --name influxdb -p 8086:8086 \
  -e DOCKER_INFLUXDB_INIT_MODE=setup \
  -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
  -e DOCKER_INFLUXDB_INIT_PASSWORD=my_strong_password \
  -e DOCKER_INFLUXDB_INIT_ORG=my_org \
  -e DOCKER_INFLUXDB_INIT_BUCKET=network_forensics \
  influxdb:2.7

# 2. Start Grafana (The Dashboard)
docker run -d --name grafana --link influxdb -p 3000:3000 grafana/grafana-oss
```

### 2\. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3\. Configuration

Before running, open `api.py` and `export_data.py`. Update the `INFLUX_TOKEN` variable with the token generated from your InfluxDB instance (Found at `http://localhost:8086` -\> Data -\> API Tokens).

```python
INFLUX_TOKEN = "your-generated-token-here"
```

## 💻 Usage

### 1\. Start the Ingestion API

Start the server to begin listening for network traffic logs.

```bash
uvicorn api:app --reload
```

  * **Docs:** Access the interactive API documentation at `http://localhost:8000/docs`

### 2\. Simulate Traffic (Testing)

To verify the pipeline without live traffic, run the simulation script. This mimics devices like *Smart Baby Monitors* and *Infusion Pumps*.

```bash
python simulate_traffic.py
```

### 3\. Export Data for Training

To generate a dataset for the Machine Learning team (CSV format):

```bash
python export_data.py
```

  * **Output:** Creates `ciciot2023_training_data.csv` containing all features and anomaly flags.

## 📊 Visualization (Grafana)

1.  Open `http://localhost:3000` (Login: `admin`/`admin`).
2.  Add Data Source -\> **InfluxDB**.
      * **URL:** `http://influxdb:8086`
      * **Organization:** `my_org`
      * **Token:** (Your API Token)
      * **Bucket:** `network_forensics`
3.  Create a **Bar Chart** panel with the following Flux query to see failing devices:

<!-- end list -->

```sql
from(bucket: "network_forensics")
  |> range(start: v.timeRangeStart)
  |> filter(fn: (r) => r["_measurement"] == "iomt_traffic")
  |> filter(fn: (r) => r["_field"] == "is_anomaly" and r["_value"] == 1)
  |> group(columns: ["device_type"])
  |> count()
  |> keep(columns: ["_value", "device_type"])
  |> rename(columns: {_value: "Total Anomalies", device_type: "Device"})
  |> sort(columns: ["Total Anomalies"], desc: true)
```