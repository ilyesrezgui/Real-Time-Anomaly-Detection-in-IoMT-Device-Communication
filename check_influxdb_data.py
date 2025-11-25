"""
Script to check if data is being stored in InfluxDB
"""
from influxdb_client import InfluxDBClient

# Configuration from your consumer
INFLUXDB_URL = 'http://localhost:8086'
INFLUXDB_TOKEN = 'bLu6eS4fYfeFdnQv6ZZ4lyWObXncoDjN0bW8rxaVm_EVbe0_bzcRkFVlTP_ZEAgDZT26HBLNF9BVBA9aV36aFw=='
INFLUXDB_ORG = 'OST'
INFLUXDB_BUCKET = 'iomt_data'

print("Connecting to InfluxDB...")
print(f"URL: {INFLUXDB_URL}")
print(f"Org: {INFLUXDB_ORG}")
print(f"Bucket: {INFLUXDB_BUCKET}")
print("-" * 60)

try:
    # Initialize client
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

    # Check connection
    print("\n✓ Successfully connected to InfluxDB!")

    # Query API
    query_api = client.query_api()

    # Query to get the last 10 records
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -1h)
      |> limit(n: 10)
    '''

    print(f"\nQuerying last 10 records from the past hour...")
    print("-" * 60)

    # Execute query
    tables = query_api.query(query, org=INFLUXDB_ORG)

    if not tables:
        print("\n⚠ No data found in the bucket.")
        print("This could mean:")
        print("  1. Data hasn't been written yet")
        print("  2. The consumer hasn't started writing to InfluxDB")
        print("  3. Data is older than 1 hour")
    else:
        print(f"\n✓ Found data! Showing first 10 records:\n")
        record_count = 0
        for table in tables:
            for record in table.records:
                record_count += 1
                print(f"Record {record_count}:")
                print(f"  Time: {record.get_time()}")
                print(f"  Measurement: {record.get_measurement()}")
                print(f"  Field: {record.get_field()}")
                print(f"  Value: {record.get_value()}")
                print(f"  Tags: {record.values}")
                print()

        print(f"Total records shown: {record_count}")

    # Get bucket statistics
    print("\n" + "=" * 60)
    print("Bucket Statistics:")
    print("=" * 60)

    stats_query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -24h)
      |> count()
    '''

    stats_tables = query_api.query(stats_query, org=INFLUXDB_ORG)

    if stats_tables:
        print("\nData points in last 24 hours:")
        for table in stats_tables:
            for record in table.records:
                print(f"  {record.get_field()}: {record.get_value()} points")

    client.close()
    print("\n✓ Connection closed successfully!")

except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Make sure InfluxDB is running: docker ps | grep influxdb")
    print("  2. Check if the token is correct")
    print("  3. Verify the organization and bucket exist")
    print("  4. Make sure the consumer has written data")
