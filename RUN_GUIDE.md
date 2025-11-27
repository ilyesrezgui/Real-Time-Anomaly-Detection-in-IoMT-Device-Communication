# Real-Time Anomaly Detection System - Run Guide

## System Overview

This system processes IoMT (Internet of Medical Things) network traffic data in real-time to detect anomalies using:
- **Kafka**: Message broker for streaming data (Dockerized)
- **Spark**: Stream processing engine (Dockerized)
- **InfluxDB**: Time-series database for storing results (Dockerized)
- **Grafana**: Visualization dashboard (Dockerized)
- **LSTM Autoencoder**: ML model for anomaly detection
- **Kafka Producer**: Sends data from host machine (runs in venv)

---

## Prerequisites

### 1. Required Services (Docker)
- Kafka (port 9092 for host, 29092 for Docker network)
- Zookeeper (port 2181)
- InfluxDB (port 8086)
- Grafana (port 3000)
- Spark Consumer (Dockerized, runs automatically with docker-compose)

### 2. Python Environment (for Kafka Producer only)
- Python 3.11.6 (in virtual environment)
- Only required for running the Kafka Producer
- Spark Consumer runs in Docker and doesn't need local Python setup

**To set up the Python environment:**
```bash
# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
or venv/bin/activate.bat
# Install all required packages
pip install -r requirements.txt
```

**Key packages for producer:**
- `kafka-python==2.0.2` - Kafka producer
- `pandas==2.3.3` & `numpy==1.24.3` - Data loading

**Note:** The Spark consumer runs in Docker with its own dependencies (see `requirements-spark.txt` and `Dockerfile.spark`)

### 3. Data Files
- `data.csv` - IoMT network traffic dataset (in project root)
- `Spark/scaler.pkl` - Feature scaler (MinMaxScaler, 31 features)
- `Spark/selected_features.json` - Selected feature list (31 features)
- `Models/Chaima/lstm_autoencoder.h5` - Trained LSTM model
- `Models/Chaima/threshold.json` - Anomaly detection threshold

---

## Initial Setup (First Time Only)

If this is your first time running the system, complete these setup steps:

### 1. Install Python Dependencies

```bash
# Navigate to project directory
cd /home/chaima/Documents/Real-Time-Anomaly-Detection-in-IoMT-Device-Communication

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install all required packages from requirements.txt
pip install -r requirements.txt
```

**This will install:**
- All Python packages with correct versions
- Kafka, Spark, InfluxDB, TensorFlow dependencies
- Compatible package versions (numpy 1.24.3 for TensorFlow 2.13)

### 2. Verify Installation

```bash
# Check key packages
pip list | grep -E "(pyspark|kafka|influxdb|tensorflow)"

# Expected output:
# influxdb-client    1.38.0
# kafka-python       2.0.2
# pyspark            3.4.1
# tensorflow         2.13.0
```

### 3. Verify Data Files Exist

```bash
# Check required files
ls -lh data.csv
ls -lh Spark/scaler.pkl
ls -lh Spark/selected_features.json
ls -lh Models/Chaima/lstm_autoencoder.h5
```

---

## Step-by-Step Instructions

### STEP 1: Start Docker Services

```bash
# Navigate to project directory
cd /home/chaima/Documents/Real-Time-Anomaly-Detection-in-IoMT-Device-Communication

# Start Docker services
docker-compose up -d

# Wait 15 seconds for services to fully initialize
sleep 15

# Verify services are running
docker ps
```

**Expected Output:**
```
NAMES             STATUS          PORTS
spark-consumer    Up XX seconds
kafka             Up XX seconds   0.0.0.0:9092->9092/tcp, 0.0.0.0:29092->29092/tcp
grafana           Up XX seconds   0.0.0.0:3000->3000/tcp
influxdb          Up XX seconds   0.0.0.0:8086->8086/tcp
zookeeper         Up XX seconds   0.0.0.0:2181->2181/tcp
```

**Important Notes:**
- The **spark-consumer** is now Dockerized and starts automatically!
- If services fail to start, run: `docker-compose down && docker-compose up -d`
- Wait at least 15-20 seconds for Kafka and Spark to fully initialize before starting the producer
- Check Spark consumer logs with: `docker logs spark-consumer`

---

### STEP 2: Start Kafka Producer

**Note:** The Spark Consumer is already running in Docker! You only need to start the producer.

Open **1 terminal window** for the Kafka Producer:

---

### STEP 3: Start Kafka Producer

```bash
# Navigate to project root
cd /home/chaima/Documents/Real-Time-Anomaly-Detection-in-IoMT-Device-Communication

# Activate virtual environment
source venv/bin/activate

# Verify you're in the right directory (should show data.csv)
ls data.csv

# Run the producer
python Kafka/producer.py
```

**Expected Output:**
```
Loading data from data.csv...
Dataset loaded. Total records: 428161
Kafka Producer initialized, connecting to localhost:9092...
Sent 1000 records to Kafka...
Sent 2000 records to Kafka...
Sent 3000 records to Kafka...
...
```

**What it does:**
- Reads `data.csv` from the project root
- Sends records to Kafka topic `iomt_traffic_stream`
- Delay: 0.01 seconds between messages (~100 records/second)

---

### STEP 4: Monitor Spark Consumer (Optional)

The Spark Consumer is running automatically in Docker. To view its real-time logs:

```bash
# View live logs from Spark Consumer
docker logs -f spark-consumer

# Or view last 50 lines
docker logs spark-consumer --tail 50
```

**Expected Output:**
```
Creating Spark Session...
Spark Session created successfully!
Connected to Kafka successfully...
Processing stream...

-------------------------------------------
Batch: 0
-------------------------------------------
[Streaming data will appear here with field values]
```

**What it does:**
- Reads streaming data from Kafka topic `iomt_traffic_stream` (via Docker network on port 29092)
- Parses JSON messages into structured data
- Displays real-time data in Docker logs
- Writes processed data to InfluxDB
- Computes and displays statistics (10-second windows)

**Press Ctrl+C** to stop following logs (the consumer keeps running in Docker)

---

## Monitoring the System

### Check InfluxDB Data

**Method 1: Web UI**
```
Open browser: http://localhost:8086
Login credentials:
  - Username: admin
  - Password: 12345678
  - Organization: OST
  - Bucket: iomt_data
```

**Method 2: Python Script**
```bash
# From project root with venv activated
python check_influxdb_data.py
```

This script shows:
- Latest 10 records from InfluxDB
- Data fields being stored
- Statistics on data points

### Visualize with Grafana

```
Open browser: http://localhost:3000
Default credentials:
  - Username: admin
  - Password: 12345678
```

To set up InfluxDB in Grafana:
1. Go to Configuration → Data Sources
2. Add InfluxDB data source
3. Configure:
   - URL: `http://influxdb:8086`
   - Organization: `OST`
   - Token: (from InfluxDB token)
   - Bucket: `iomt_data`
4. Create dashboards to visualize metrics

---

## Stopping the System

Stop in this order:

### 1. Stop Kafka Producer
```bash
# In the producer terminal, press Ctrl+C or wait for completion
```

### 2. Stop Docker Services (includes Spark Consumer)
```bash
# Navigate to project root
cd /home/chaima/Documents/Real-Time-Anomaly-Detection-in-IoMT-Device-Communication

# Stop all services (Spark Consumer, Kafka, InfluxDB, Grafana, Zookeeper)
docker-compose down
```

**Note:**
- Stopping Docker will clear all data unless volumes are persisted
- The Spark Consumer stops automatically when you run `docker-compose down`
- To keep services running but stop the producer, just stop the producer terminal (Ctrl+C)

---

## Troubleshooting

### Issue: "Kafka connection refused" or "Broker may not be available"

**Solution:**
```bash
# Restart Docker services cleanly
docker-compose down
sleep 5
docker-compose up -d
sleep 15  # Wait for Kafka to initialize

# Verify Kafka is running
docker ps | grep kafka
```

### Issue: "Cannot find data.csv"

**Cause:** Running producer from wrong directory

**Solution:**
```bash
# CORRECT: Run from project root
cd /home/chaima/Documents/Real-Time-Anomaly-Detection-in-IoMT-Device-Communication
source venv/bin/activate
python Kafka/producer.py

# WRONG: Don't run from inside Kafka directory
cd Kafka && python producer.py  # This will fail
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Verify correct Python
which python  # Should show path to venv/bin/python

# Reinstall packages if needed
pip install -r requirements.txt
```

### Issue: Spark consumer not starting or crashing

**Cause:** Container build issue or Java/Spark incompatibility

**Solution:**
```bash
# Rebuild the Spark consumer image
docker-compose build spark-consumer

# Restart all services
docker-compose down
docker-compose up -d

# Check logs for errors
docker logs spark-consumer --tail 100
```

### Issue: InfluxDB "401 Unauthorized"

**Cause:** Incorrect token or credentials

**Solution:**
1. Check token in `docker-compose.yml` under spark-consumer environment variables
2. Or regenerate token in InfluxDB UI at http://localhost:8086
3. Update the INFLUXDB_TOKEN in docker-compose.yml

### Issue: Spark Consumer shows "UnknownTopicOrPartitionException"

**Cause:** Kafka topic hasn't been created yet (producer not started)

**Solution:**
```bash
# Start the Kafka producer first to create the topic
source venv/bin/activate
python Kafka/producer.py

# The Spark consumer will automatically connect once topic exists
```

---

## Configuration Files

### Docker Services (docker-compose.yml)
```yaml
- Kafka: localhost:9092 (host access), kafka:29092 (Docker network)
- Zookeeper: localhost:2181
- InfluxDB: localhost:8086
- Grafana: localhost:3000
- Spark Consumer: Runs in Docker, connects via internal network
```

**InfluxDB Credentials:**
- Username: `admin`
- Password: `12345678`
- Organization: `OST`
- Bucket: `iomt_data`

**Grafana Credentials:**
- Username: `admin`
- Password: `12345678`

### Producer Configuration (Kafka/producer.py)
```python
KAFKA_BROKER = 'localhost:9092'  # Connects from host machine
KAFKA_TOPIC = 'iomt_traffic_stream'
CSV_FILE_PATH = 'data.csv'  # Relative to project root
SIMULATION_DELAY_SECONDS = 0.01  # 100 records/second
```

### Consumer Configuration (docker-compose.yml)
The Spark Consumer is configured via environment variables in docker-compose.yml:
```yaml
environment:
  KAFKA_BROKER: kafka:29092  # Docker network connection
  KAFKA_TOPIC: iomt_traffic_stream
  INFLUXDB_URL: http://influxdb:8086  # Docker network connection
  INFLUXDB_ORG: OST
  INFLUXDB_BUCKET: iomt_data
```

### Dockerfile Configuration
- **Dockerfile.spark**: Builds Spark consumer image with Java 11 and minimal dependencies
- **requirements-spark.txt**: Contains only essential packages (pyspark, influxdb-client, etc.)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           HOST MACHINE                              │
│                                                                     │
│  data.csv → Kafka Producer (venv) → localhost:9092                 │
│                                           ↓                         │
└───────────────────────────────────────────┼─────────────────────────┘
                                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        DOCKER NETWORK                               │
│                                                                     │
│  Kafka (kafka:29092) → Spark Consumer (Docker)                     │
│         ↓                       ↓                                   │
│         └──────────────────────┴─────────→ InfluxDB (influxdb:8086)│
│                                                    ↓                │
│                                            Grafana Dashboard        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Data Flow:
1. Producer (host) → Kafka (port 9092)
2. Kafka (port 29092) → Spark Consumer (Docker)
3. Spark Consumer → InfluxDB (Docker network)
4. InfluxDB → Grafana (Docker network)
5. User accesses Grafana via localhost:3000
```

---

## Quick Start (Summary)

```bash
# FIRST TIME ONLY: Install dependencies for producer
cd /home/chaima/Documents/Real-Time-Anomaly-Detection-in-IoMT-Device-Communication
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# EVERY TIME: Run the system
# 1. Start Docker services (includes Spark Consumer automatically!)
cd /home/chaima/Documents/Real-Time-Anomaly-Detection-in-IoMT-Device-Communication
docker-compose up -d
sleep 20  # Wait for all services including Spark

# 2. Verify services are running
docker ps  # Should show 5 containers: spark-consumer, kafka, zookeeper, influxdb, grafana

# 3. Start Producer (in terminal or background)
source venv/bin/activate
python Kafka/producer.py

# 4. Monitor (Optional)
docker logs -f spark-consumer        # Watch Spark Consumer logs
python check_influxdb_data.py        # Check InfluxDB data
# Browser: http://localhost:8086      # InfluxDB UI
# Browser: http://localhost:3000      # Grafana Dashboard

# 5. Stop everything when done
# Press Ctrl+C to stop producer
docker-compose down  # Stops all Docker services
```

---

## Performance Notes

- **Data Rate**: ~100 records/second (configurable via `SIMULATION_DELAY_SECONDS`)
- **Processing**: Spark processes data in micro-batches (default interval)
- **Storage**: InfluxDB stores all processed records with timestamps
- **Window Statistics**: 10-second aggregation windows with watermark
- **NULL Values**: Normal in CSV data - different protocols have different fields

---

## Data Being Stored

### InfluxDB Measurement: `iomt_traffic`

**Tags:**
- `label`: Traffic type (BENIGN, DOS-TCP_FLOOD, DDOS-ICMP_FLOOD, etc.)
- `protocol`: Protocol type (0, 6, 17, etc.)

**Fields:**
- `header_length`: IP header length
- `time_to_live`: TTL value
- `rate`: Packet rate
- `tot_sum`: Total packet sum
- `avg`: Average packet size
- `std`: Standard deviation
- `variance`: Packet variance
- `iat`: Inter-arrival time

**Timestamps:** Microsecond precision

---

## Docker Configuration Files

### Key Files for Dockerization:
- **Dockerfile.spark**: Docker image definition for Spark consumer
  - Base: python:3.11-slim
  - Java: Adoptium Temurin 11 JRE (required for PySpark 3.4.1)
  - Dependencies: requirements-spark.txt

- **requirements-spark.txt**: Minimal dependencies for Spark consumer
  - pyspark==3.4.1
  - influxdb-client==1.38.0
  - Core dependencies only (no heavy ML packages)

- **docker-compose.yml**: Multi-container orchestration
  - Defines 5 services: zookeeper, kafka, influxdb, grafana, spark-consumer
  - Configures dual Kafka listeners (host + Docker network)
  - Sets environment variables for Spark consumer

- **Spark/consumer.py**: Updated to use environment variables for Docker compatibility

### Helper Scripts:
- `Spark/check_model_and_features.py` - Verification tool
- `check_influxdb_data.py` - Query InfluxDB data

---

## Support & Resources

### Verify Installation
```bash
# Check Python packages
pip list | grep -E "(kafka|pyspark|influxdb|tensorflow)"

# Check Docker services
docker-compose ps

# Check data file
ls -lh data.csv
```

### Logs
```bash
# Docker service logs
docker logs spark-consumer       # Spark Consumer (most important)
docker logs kafka               # Kafka broker
docker logs influxdb            # InfluxDB
docker logs grafana             # Grafana

# Follow logs in real-time
docker logs -f spark-consumer

# View all service logs together
docker-compose logs -f
```

### Common Issues
1. **Kafka not connecting**: Restart Docker services with `docker-compose down && docker-compose up -d`
2. **Spark consumer not starting**: Check logs with `docker logs spark-consumer`, rebuild with `docker-compose build spark-consumer`
3. **Port conflicts**: Check no other services on 9092, 8086, 3000, 29092
4. **Permission errors** (producer): Ensure venv is activated with `source venv/bin/activate`

---

## Success Indicators

✅ **Docker Services**: All 5 containers running (use `docker ps`)
✅ **Spark Consumer**: Logs show "Batch: X" with data (use `docker logs spark-consumer`)
✅ **Producer**: Sending records every 0.01 seconds (shows "Sent XXXX records...")
✅ **InfluxDB**: Data visible via check script or web UI
✅ **No errors**: Only warnings (WARNs) are acceptable in logs

**Your system is working when:**
- `docker ps` shows 5 running containers (spark-consumer, kafka, zookeeper, influxdb, grafana)
- Producer terminal shows "Sent XXXX records to Kafka..."
- `docker logs spark-consumer` shows batch processing with field values
- `python check_influxdb_data.py` returns records
- InfluxDB UI (http://localhost:8086) shows data in `iomt_data` bucket
- Grafana (http://localhost:3000) can query InfluxDB data source
