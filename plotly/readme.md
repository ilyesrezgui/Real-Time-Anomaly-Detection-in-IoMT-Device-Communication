# Real-Time IoMT Traffic datat visualitation 
this part create the visualization of the data sourced from a kafka consumer it uses plotly to analyze the data and showcase the result of isolation forest model
---

## Prerequisites

* **Docker** and **Docker Compose** installed on your system.
* **Python 3.x** installed.

---

## Setup and Execution

follow previous instruction to start the kafka docker and initiate it producer
build the docker image: docker build -t streamlit-app .
create a network: docker network create kafka-net
connect the network to kafka containe: docker network connect kafka-net kafka
run the website: docker run -p 8502:8501 --name streamlit-app --network kafka-net streamlit-app



### Result
check the screen shot for results