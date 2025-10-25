import pandas as pd
import json
import time
from kafka import KafkaProducer

# --- Configuration ---
KAFKA_BROKER = 'localhost:9092'  # the Kafka server (localhost:9092). This is where the producer will send the messages.
KAFKA_TOPIC = 'iomt_traffic_stream' #The name of the Kafka topic (iomt_traffic_stream) to which the simulated IoMT data will be published.
CSV_FILE_PATH = 'data.csv'
SIMULATION_DELAY_SECONDS = 0.01  #A small delay (0.01 seconds) introduced after sending each record to Kafka.

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

    # Initialize the Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=json_serializer
    )
    print(f"Kafka Producer initialized, connecting to {KAFKA_BROKER}...")

    # Iterate through the DataFrame rows
    for index, row in df.iterrows():
        # Convert the row (Pandas Series) to a dictionary
        message = row.to_dict()

        # The 'Label' column identifies Normal vs. Attack; it should be passed along.
        # Ensure numerical data types are handled correctly (Pandas handles this conversion).

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
    # Ensure your Kafka cluster is running (using the docker-compose setup provided previously)
    simulate_iomt_traffic()