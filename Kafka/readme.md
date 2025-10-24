## Real-Time IoMT Traffic Simulation

This part simulates real-time IoMT device communication using Kafka (Producer–Consumer architecture). It replays IoMT dataset traffic in real time and allows you to monitor it.

---

### Step 1: Run Docker Compose

Start Zookeeper and Kafka using the `docker-compose.yml` file:

```bash
docker-compose up -d
