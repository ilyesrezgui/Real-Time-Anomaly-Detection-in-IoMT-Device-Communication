### Step 1: Run Docker Compose

Run the `docker-compose.yml` file to start Zookeeper and Kafka:

```bash
docker-compose up -d

You cna check on the docker app that the containers are running fine.
You just run the python producer code and it is going to start sending the data in real time by batches of 1000.


In order to verify that the data is being sent ocrrectly by the producer, we can check with :
```bash
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic iomt_traffic_stream --from-beginning
