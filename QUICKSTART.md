# 🚀 Quick Start Guide

## Run the Entire Application with One Command

### Prerequisites
- **Docker** and **Docker Compose** installed
- That's it! No Python or other dependencies needed

### Start Everything
```bash
docker-compose up -d
```

This single command starts all 6 services:
1. ✅ Zookeeper
2. ✅ Kafka
3. ✅ InfluxDB (with pre-configured token)
4. ✅ Grafana
5. ✅ Kafka Producer (sends IoMT data)
6. ✅ Spark Consumer (detects anomalies)

**Note**: The InfluxDB token is now pre-configured in `docker-compose.yml`, so everything works out of the box!

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker logs -f kafka-producer
docker logs -f spark-consumer
```

### Access Dashboards

**Grafana**: http://localhost:3000
- Username: `admin`
- Password: `12345678`

**InfluxDB**: http://localhost:8086
- Username: `admin`
- Password: `12345678`

### Stop Everything
```bash
docker-compose down
```

## For Your Teammate

Share these instructions with your teammate:

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Real-Time-Anomaly-Detection-in-IoMT-Device-Communication
   ```

2. **Run it** (works on Windows, Mac, Linux)
   ```bash
   docker-compose up -d
   ```

3. **Done!** Access the services:
   - Grafana: http://localhost:3000 (admin/12345678)
   - InfluxDB: http://localhost:8086 (admin/12345678)

## Verify Data is Being Written

### Check InfluxDB has data:
```bash
docker exec influxdb influx query \
  'from(bucket:"iomt_data") |> range(start: -5m) |> count()' \
  --org OST --token my-super-secret-admin-token
```

You should see data counts for various fields.

### Check anomaly detection results:
```bash
docker exec influxdb influx query \
  'from(bucket:"iomt_data") |> range(start: -5m) |> filter(fn: (r) => r["_field"] == "reconstruction_error")' \
  --org OST --token my-super-secret-admin-token
```

## Troubleshooting

### Port conflicts?
```bash
# Check what's using ports
netstat -an | grep "9092\|8086\|3000"

# Stop the application and change ports in docker-compose.yml if needed
```

**Rebuild after code changes:**
```bash
docker-compose build
docker-compose up -d
```

**Fresh start:**
```bash
docker-compose down -v
docker-compose up -d
```

## What's Running?

| Service | What it does | Port |
|---------|-------------|------|
| Kafka | Message broker | 9092 |
| Zookeeper | Kafka coordination | 2181 |
| InfluxDB | Time-series database | 8086 |
| Grafana | Visualization | 3000 |
| Producer | Sends IoMT data to Kafka | - |
| Consumer | Spark + LSTM anomaly detection | - |

## Architecture

```
data.csv → Kafka Producer → Kafka → Spark Consumer → InfluxDB → Grafana
                                          ↓
                                   LSTM Autoencoder
                                   (Anomaly Detection)
```

## How Anomaly Detection Works

- **Model**: LSTM Autoencoder (Models/Chaima/lstm_autoencoder.h5)
- **Features**: 31 network traffic features
- **Threshold**: 0.1435 (reconstruction error)
- **Output**: Each data point tagged as `predicted_anomaly: true/false`

**Normal traffic**: Low reconstruction error (< 0.1435)
**Anomalous traffic**: High reconstruction error (> 0.1435)

## Next Steps

1. Open Grafana at http://localhost:3000
2. Configure InfluxDB data source
3. Create dashboards to visualize:
   - Anomaly detection results
   - Traffic patterns
   - Attack types distribution
   - Real-time metrics

## Development

Want to modify the code?

1. Edit files locally
2. Rebuild: `docker-compose build`
3. Restart: `docker-compose up -d`

No need to install Python packages on your machine!
