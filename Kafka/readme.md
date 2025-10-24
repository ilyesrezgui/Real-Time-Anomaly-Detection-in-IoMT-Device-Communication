## Real-Time IoMT Traffic Simulation

This part simulates real-time IoMT device communication using Kafka (Producer–Consumer architecture). It replays IoMT dataset traffic in real time and allows you to monitor it.

---

### Step 1: Run Docker Compose

Start Zookeeper and Kafka using the `docker-compose.yml` file:

```bash
docker-compose up -d


### Step 2: Run the Python Producer

Run the Python script that acts as the Kafka producer.  
It will send the IoMT dataset in **batches of 1000 records** to the Kafka topic.

```bash
python producer.py
