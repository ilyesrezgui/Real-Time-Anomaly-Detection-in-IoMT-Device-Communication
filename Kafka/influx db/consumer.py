from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import time

# ----------------------
# Kafka Configuration
# ----------------------

CONSUMER_GROUP = 'iomt_consumer_group'  # <-- add this line
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'iomt_traffic_stream'
# --- InfluxDB Config ---

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "fpQW8sZYT3xv_kSM0N1lhTWqFhWyawfSu5_qGmYpylJUFsxujvMAWWYM3BMMw38gdKUWkVXcH1Cxsm_M6AIrcA=="
INFLUX_ORG = "OST"
INFLUX_BUCKET = "iomt_data"  # <-- add this line

# ----------------------
# Initialize Kafka Consumer
# ----------------------
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=CONSUMER_GROUP
)

# ----------------------
# Initialize InfluxDB Client
# ----------------------
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

print(f"Consuming from Kafka topic '{KAFKA_TOPIC}' and writing to InfluxDB bucket '{INFLUX_BUCKET}'...")

# ----------------------
# Consume messages and write to InfluxDB
# ----------------------
for message in consumer:
    data = message.value  # Kafka message as Python dict

    # Create a Point for InfluxDB
    point = Point("iomt_measurement")  # Measurement name
    for key, value in data.items():
        if isinstance(value, (int, float)):
            point.field(key, value)        # Numeric fields
        else:
            point.tag(key, str(value))     # Non-numeric fields as tags

    # Timestamp in nanoseconds
    point.time(time.time_ns(), write_precision=WritePrecision.NS)

    # Write to InfluxDB
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    # Optional: print to console
    print(f"Written to InfluxDB: {data}")
