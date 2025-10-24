# Real-Time IoMT Traffic Simulation 

This project simulates real-time Internet of Medical Things (**IoMT**) device communication using a **Kafka Producer-Consumer architecture** within a Dockerized environment. It replays IoMT dataset traffic in real time for monitoring and analysis.

---

## Prerequisites

* **Docker** and **Docker Compose** installed on your system.
* **Python 3.x** installed.
* Required Python libraries (e.g., `kafka-python`) installed (typically via `pip install -r requirements.txt`).

---

## Setup and Execution

Follow these steps to set up and run the real-time simulation.

### Step 1: Start Zookeeper and Kafka (Docker Compose)

Start the **Zookeeper** and **Kafka Broker** services using the `docker-compose.yml` file.
````
docker-compose up -d
````

### Step 2 : Run the IoMT Traffic Producer
Execute the Python script (producer.py), which acts as the Kafka Producer. It reads the IoMT dataset and sends the records to the iomt_traffic_stream topic in batches of 1000 records to simulate real-time traffic flow.

````
cd..
python kafka\producer.py
````
### Step 3: Verify Data is Being Sent (Console Consumer)
To monitor the data flow and verify that the producer is sending messages correctly, use the Kafka console consumer running inside the Kafka Docker container. This command subscribes to the iomt_traffic_stream topic and displays messages in real-time.

````
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic iomt_traffic_stream --from-beginning
````
