from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, count, stddev, max as spark_max, min as spark_min
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import sys

# --- Configuration ---
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'iomt_traffic_stream'
INFLUXDB_URL = 'http://localhost:8086'
INFLUXDB_TOKEN = 'bLu6eS4fYfeFdnQv6ZZ4lyWObXncoDjN0bW8rxaVm_EVbe0_bzcRkFVlTP_ZEAgDZT26HBLNF9BVBA9aV36aFw=='  # Get this from InfluxDB UI
INFLUXDB_ORG = 'OST'
INFLUXDB_BUCKET = 'iomt_data'

# Define the schema matching your CSV data structure
iomt_schema = StructType([
    StructField("Header_Length", DoubleType(), True),
    StructField("Protocol Type", IntegerType(), True),
    StructField("Time_To_Live", IntegerType(), True),
    StructField("Rate", DoubleType(), True),
    StructField("fin_flag_number", IntegerType(), True),
    StructField("syn_flag_number", IntegerType(), True),
    StructField("rst_flag_number", IntegerType(), True),
    StructField("psh_flag_number", IntegerType(), True),
    StructField("ack_flag_number", IntegerType(), True),
    StructField("ece_flag_number", IntegerType(), True),
    StructField("cwr_flag_number", IntegerType(), True),
    StructField("ack_count", IntegerType(), True),
    StructField("syn_count", IntegerType(), True),
    StructField("fin_count", IntegerType(), True),
    StructField("rst_count", IntegerType(), True),
    StructField("HTTP", IntegerType(), True),
    StructField("HTTPS", IntegerType(), True),
    StructField("DNS", IntegerType(), True),
    StructField("Telnet", IntegerType(), True),
    StructField("SMTP", IntegerType(), True),
    StructField("SSH", IntegerType(), True),
    StructField("IRC", IntegerType(), True),
    StructField("TCP", IntegerType(), True),
    StructField("UDP", IntegerType(), True),
    StructField("DHCP", IntegerType(), True),
    StructField("ARP", IntegerType(), True),
    StructField("ICMP", IntegerType(), True),
    StructField("IGMP", IntegerType(), True),
    StructField("IPv", IntegerType(), True),
    StructField("LLC", IntegerType(), True),
    StructField("Tot sum", DoubleType(), True),
    StructField("Min", DoubleType(), True),
    StructField("Max", DoubleType(), True),
    StructField("AVG", DoubleType(), True),
    StructField("Std", DoubleType(), True),
    StructField("Tot size", DoubleType(), True),
    StructField("IAT", DoubleType(), True),
    StructField("Number", IntegerType(), True),
    StructField("Variance", DoubleType(), True),
    StructField("Label", StringType(), True),  # Normal or Attack label
])

def create_spark_session():
    """
    Initialize Spark Session with Kafka integration
    """
    print("Creating Spark Session...")
    print("This may take a minute on first run (downloading Kafka connector JAR)...")
    
    spark = SparkSession.builder \
        .appName("IoMT-Anomaly-Detection-Stream") \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    print("Spark Session created successfully!")
    return spark

def read_from_kafka(spark):
    """
    Read streaming data from Kafka
    """
    kafka_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()
    
    return kafka_df

def process_stream(kafka_df):
    """
    Parse JSON messages and apply transformations
    """
    # Parse the JSON value from Kafka
    parsed_df = kafka_df.select(
        from_json(col("value").cast("string"), iomt_schema).alias("data")
    ).select("data.*")
    
    # Add a timestamp for windowing operations
    from pyspark.sql.functions import current_timestamp
    parsed_df = parsed_df.withColumn("event_time", current_timestamp())
    
    return parsed_df

def write_to_influxdb(batch_df, batch_id):
    """
    Write processed data to InfluxDB
    Uses InfluxDB Line Protocol
    """
    try:
        from influxdb_client import InfluxDBClient, Point
        from influxdb_client.client.write_api import SYNCHRONOUS
        
        # Initialize InfluxDB client
        client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        # Convert DataFrame to list of dictionaries
        records = batch_df.collect()
        
        # Write each record as a point
        for record in records:
            point = Point("iomt_traffic") \
                .tag("label", record["Label"]) \
                .tag("protocol", str(record["Protocol Type"])) \
                .field("header_length", float(record["Header_Length"]) if record["Header_Length"] else 0.0) \
                .field("time_to_live", int(record["Time_To_Live"]) if record["Time_To_Live"] else 0) \
                .field("rate", float(record["Rate"]) if record["Rate"] else 0.0) \
                .field("tot_sum", float(record["Tot sum"]) if record["Tot sum"] else 0.0) \
                .field("avg", float(record["AVG"]) if record["AVG"] else 0.0) \
                .field("std", float(record["Std"]) if record["Std"] else 0.0) \
                .field("variance", float(record["Variance"]) if record["Variance"] else 0.0) \
                .field("iat", float(record["IAT"]) if record["IAT"] else 0.0)
            
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        
        print(f"Batch {batch_id}: Written {len(records)} records to InfluxDB")
        client.close()
        
    except Exception as e:
        print(f"Error writing to InfluxDB: {str(e)}")

def write_to_console(df):
    """
    Write stream to console for debugging
    """
    query = df \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .option("numRows", 10) \
        .start()
    
    return query

def write_stream_to_influxdb(df):
    """
    Write streaming data to InfluxDB using foreachBatch
    """
    query = df \
        .writeStream \
        .foreachBatch(write_to_influxdb) \
        .outputMode("append") \
        .option("checkpointLocation", "/tmp/spark-checkpoint") \
        .start()
    
    return query

def compute_statistics(df):
    """
    Compute real-time statistics for monitoring
    """
    stats_df = df \
        .withWatermark("event_time", "10 seconds") \
        .groupBy(
            window(col("event_time"), "10 seconds"),
            col("Label")
        ) \
        .agg(
            count("*").alias("count"),
            avg("Rate").alias("avg_rate"),
            stddev("Rate").alias("std_rate"),
            avg("Header_Length").alias("avg_header_length"),
            spark_max("Tot sum").alias("max_tot_sum"),
            spark_min("Tot sum").alias("min_tot_sum"),
            avg("Variance").alias("avg_variance")
        )
    
    return stats_df

def main():
    """
    Main function to run the Spark streaming application
    """
    print("Starting IoMT Anomaly Detection Spark Consumer...")
    
    # Create Spark session
    spark = create_spark_session()
    
    # Read from Kafka
    kafka_df = read_from_kafka(spark)
    print("Connected to Kafka successfully...")
    
    # Process the stream
    processed_df = process_stream(kafka_df)
    print("Processing stream...")
    
    # Compute statistics
    stats_df = compute_statistics(processed_df)
    
    # Write to console for debugging
    console_query = write_to_console(processed_df)
    
    # Write to InfluxDB
    influx_query = write_stream_to_influxdb(processed_df)
    
    # Write statistics to console
    stats_query = write_to_console(stats_df)
    
    print("\nSpark Streaming started successfully!")
    print("Waiting for data from Kafka...")
    print("Press Ctrl+C to stop the application\n")
    
    # Await termination
    try:
        spark.streams.awaitAnyTermination()
    except KeyboardInterrupt:
        print("\n\nStopping streams gracefully...")
        console_query.stop()
        influx_query.stop()
        stats_query.stop()
        spark.stop()
        print("Application stopped.")

if __name__ == "__main__":
    main()