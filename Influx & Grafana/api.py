import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIG ---
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "V1fkkMGh_53RbZJssjTUeipVcgJNcc5Z2RSpkHefCB77eTfCJJoWKgfRE0mDQmhclr-fgFmDcNx_9l7OF4D30Q==" 
INFLUX_ORG = "my_org"
INFLUX_BUCKET = "network_forensics"

# --- DEVICE MAPPING (Solves "Which Machine?") ---
# In a real scenario, this comes from your inventory database.
DEVICE_MAP = {
    "192.168.10.14": "Smart_Thermostat",
    "192.168.10.15": "Smart_Baby_Monitor",
    "192.168.10.16": "Security_Camera",
    "192.168.10.24": "Infusion_Pump_A",
    "192.168.10.50": "MRI_Scanner_Control"
}

# --- DATA MODEL (CICIoT2023 Features) ---
class CicIotData(BaseModel):
    timestamp: datetime
    src_ip: str
    protocol: str
    label: str  # "Benign" or Attack Name

    # Key Numerical Features from Dataset
    flow_duration: float
    tot_size: float
    rate: float
    srate: float
    drate: float
    iat: float
    magnitude: float
    radius: float
    covariance: float
    variance: float
    weight: float

    # Flag Counts
    syn_count: float
    ack_count: float
    rst_count: float
    fin_count: float

    # ML Model Result
    reconstruction_error: float
    is_anomaly: bool

app = FastAPI()
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

@app.post("/log_traffic")
async def log_traffic(data: CicIotData):
    # 1. Identify the device type
    dev_type = DEVICE_MAP.get(data.src_ip, "Unknown_Device")

    # 2. Create the InfluxDB Point
    p = Point("iomt_traffic") \
        .time(data.timestamp, WritePrecision.NS) \
        .tag("device_ip", data.src_ip) \
        .tag("device_type", dev_type) \
        .tag("protocol", data.protocol) \
        .tag("attack_label", data.label) \
        .field("reconstruction_error", data.reconstruction_error) \
        .field("is_anomaly", int(data.is_anomaly)) \
        .field("flow_duration", data.flow_duration) \
        .field("rate", data.rate) \
        .field("srate", data.srate) \
        .field("drate", data.drate) \
        .field("magnitude", data.magnitude) \
        .field("radius", data.radius) \
        .field("weight", data.weight)

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)
    return {"status": "logged", "device": dev_type}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)