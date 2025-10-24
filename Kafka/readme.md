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

```bash
docker-compose up -d 

