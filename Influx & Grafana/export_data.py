import pandas as pd
from influxdb_client import InfluxDBClient

# --- Configuration ---
url = "http://localhost:8086"
token = "V1fkkMGh_53RbZJssjTUeipVcgJNcc5Z2RSpkHefCB77eTfCJJoWKgfRE0mDQmhclr-fgFmDcNx_9l7OF4D30Q=="
org = "my_org"
bucket = "network_forensics"

print("Connecting to database...")
client = InfluxDBClient(url=url, token=token, org=org)

# --- The Query ---
# We use a 'pivot' to turn the data into a table format (CSV style)
# getting all data from the last 30 days.
query = f'''
from(bucket: "{bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "iomt_traffic")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

print("Fetching data (this might take a moment)...")
try:
    # This function automatically converts the InfluxDB result to a Pandas DataFrame
    df = client.query_api().query_data_frame(query, org=org)

    # Clean up internal InfluxDB columns we don't need for training
    cols_to_drop = ['result', 'table', '_start', '_stop', '_measurement']
    # Only drop columns that actually exist in the dataframe
    existing_drop_cols = [c for c in cols_to_drop if c in df.columns]
    df = df.drop(columns=existing_drop_cols)

    # Rename _time to timestamp
    if "_time" in df.columns:
        df = df.rename(columns={"_time": "timestamp"})

    # Save to CSVdata
    filename = "ciciot2023_training_.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Success! Exported {len(df)} rows to '{filename}'")

except Exception as e:
    print(f"❌ Error: {e}")