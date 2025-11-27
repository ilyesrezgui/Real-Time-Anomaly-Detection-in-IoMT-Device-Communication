
import pandas as pd
import json
import time
import os
from kafka import KafkaProducer

# --- Configuration ---
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'iomt_traffic_stream')
CSV_FILE_PATH = 'data.csv'
SIMULATION_DELAY_SECONDS = 0.01

def json_serializer(data):
    """Simple JSON serializer for Kafka messages. from Python dic to JSON formatted string to bytes"""
    return json.dumps(data).encode('utf-8')

def simulate_iomt_traffic():
    """
    Reads the IoMT data from CSV and publishes it to Kafka in real-time simulation.
    """
    print(f"Loading data from {CSV_FILE_PATH}...")
    try:
        # Load the entire dataset
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"Dataset loaded. Total records: {len(df)}")
    except FileNotFoundError:
        print(f"Error: CSV file not found at {CSV_FILE_PATH}")
        return

    # Wait for Kafka to be ready
    print(f"Waiting for Kafka to be ready at {KAFKA_BROKER}...")
    time.sleep(10)

    # Initialize the Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=json_serializer
    )
    print(f"Kafka Producer initialized, connecting to {KAFKA_BROKER}...")
    print(f"Publishing to topic: {KAFKA_TOPIC}")

    # Iterate through the DataFrame rows
    for index, row in df.iterrows():
        # Convert the row (Pandas Series) to a dictionary
        message = row.to_dict()

        # Send the message to Kafka
        producer.send(KAFKA_TOPIC, value=message)

        if index % 1000 == 0 and index > 0:
            print(f"Sent {index} records to Kafka...")

        # Simulate real-time delay
        time.sleep(SIMULATION_DELAY_SECONDS)

    # Flush the producer buffer to ensure all messages are sent
    producer.flush()
    print(f"\nSimulation complete. Total records sent: {len(df)}")

if __name__ == "__main__":
    simulate_iomt_traffic()
