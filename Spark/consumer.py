from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, count, stddev, max as spark_max, min as spark_min
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import sys
import os
import json
import joblib
import numpy as np

# Use environment variables for Docker compatibility, fallback to localhost for local runs
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'iomt_traffic_stream')
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'bLu6eS4fYfeFdnQv6ZZ4lyWObXncoDjN0bW8rxaVm_EVbe0_bzcRkFVlTP_ZEAgDZT26HBLNF9BVBA9aV36aFw==')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'OST')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'iomt_data')

# --- Anomaly Detection Model Configuration ---
# Paths to model files (in Docker container)
SCALER_PATH = '/app/scaler.pkl'
SELECTED_FEATURES_PATH = '/app/selected_features.json'
MODEL_PATH = '/app/lstm_autoencoder.h5'
THRESHOLD_PATH = '/app/threshold.json'

# Global variables to store loaded models
scaler = None
selected_features = None
model = None
threshold = None

def load_anomaly_detection_models():
    """
    Load the scaler, selected features, LSTM model, and threshold
    """
    global scaler, selected_features, model, threshold

    print("Loading anomaly detection models...")

    try:
        # Load scaler
        scaler = joblib.load(SCALER_PATH)
        print(f"✓ Loaded scaler from {SCALER_PATH}")

        # Load selected features
        with open(SELECTED_FEATURES_PATH, 'r') as f:
            selected_features = json.load(f)
        print(f"✓ Loaded {len(selected_features)} selected features")

        # Load threshold
        with open(THRESHOLD_PATH, 'r') as f:
            threshold_data = json.load(f)
            threshold = threshold_data['threshold']
        print(f"✓ Loaded threshold: {threshold}")

        # Load LSTM model (lazy load TensorFlow)
        from tensorflow import keras
        model = keras.models.load_model(MODEL_PATH)
        print(f"✓ Loaded LSTM model from {MODEL_PATH}")
        print(f"  Model input shape: {model.input_shape}")
        print(f"  Model output shape: {model.output_shape}")

        print("✓ All anomaly detection models loaded successfully!\n")
        return True

    except Exception as e:
        print(f"✗ Error loading anomaly detection models: {str(e)}")
        print("  Anomaly detection will be disabled.")
        return False

def detect_anomaly(record_dict):
    """
    Detect anomaly for a single record using LSTM autoencoder
    Returns: (is_anomaly, reconstruction_error)
    """
    global scaler, selected_features, model, threshold

    if model is None or scaler is None or selected_features is None:
        return None, None

    try:
        # Map record fields to match selected_features names
        # Handle missing features with default values
        feature_values = []
        for feature in selected_features:
            # Map feature names from selected_features to record keys
            if feature == "flow_duration":
                value = record_dict.get("Duration", 0.0)
            elif feature == "Duration":
                value = record_dict.get("Duration", 0.0)
            elif feature == "urg_count":
                value = record_dict.get("urg_count", 0)
            elif feature == "Covariance":
                value = record_dict.get("Covariance", 0.0)
            else:
                # Try direct match
                value = record_dict.get(feature, 0.0)

            # Convert None to 0.0
            if value is None:
                value = 0.0
            feature_values.append(float(value))

        # Convert to numpy array
        X = np.array([feature_values])

        # Scale features
        X_scaled = scaler.transform(X)

        # Reshape for LSTM (samples, timesteps, features)
        # LSTM expects 3D input: (batch_size, timesteps, features)
        X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

        # Get reconstruction
        X_reconstructed = model.predict(X_reshaped, verbose=0)

        # Calculate reconstruction error (MSE)
        mse = np.mean(np.power(X_reshaped - X_reconstructed, 2), axis=(1, 2))[0]

        # Determine if anomaly
        is_anomaly = mse > threshold

        return bool(is_anomaly), float(mse)

    except Exception as e:
        print(f"Error in anomaly detection: {str(e)}")
        return None, None

# Define the schema matching your CSV data structure
iomt_schema = StructType([
    StructField("Header_Length", DoubleType(), True),
    StructField("Protocol Type", IntegerType(), True),
    StructField("Time_To_Live", DoubleType(), True),
    StructField("Rate", DoubleType(), True),
    StructField("fin_flag_number", DoubleType(), True),
    StructField("syn_flag_number", DoubleType(), True),
    StructField("rst_flag_number", DoubleType(), True),
    StructField("psh_flag_number", DoubleType(), True),
    StructField("ack_flag_number", DoubleType(), True),
    StructField("ece_flag_number", DoubleType(), True),
    StructField("cwr_flag_number", DoubleType(), True),
    StructField("ack_count", IntegerType(), True),
    StructField("syn_count", IntegerType(), True),
    StructField("fin_count", IntegerType(), True),
    StructField("rst_count", IntegerType(), True),
    StructField("HTTP", DoubleType(), True),
    StructField("HTTPS", DoubleType(), True),
    StructField("DNS", DoubleType(), True),
    StructField("Telnet", DoubleType(), True),
    StructField("SMTP", DoubleType(), True),
    StructField("SSH", DoubleType(), True),
    StructField("IRC", DoubleType(), True),
    StructField("TCP", DoubleType(), True),
    StructField("UDP", DoubleType(), True),
    StructField("DHCP", DoubleType(), True),
    StructField("ARP", DoubleType(), True),
    StructField("ICMP", DoubleType(), True),
    StructField("IGMP", DoubleType(), True),
    StructField("IPv", DoubleType(), True),
    StructField("LLC", DoubleType(), True),
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
    Write processed data to InfluxDB with anomaly detection
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

        anomaly_count = 0
        normal_count = 0

        # Write each record as a point
        for record in records:
            # Convert record to dictionary for anomaly detection
            record_dict = record.asDict()

            # Perform anomaly detection
            is_anomaly, reconstruction_error = detect_anomaly(record_dict)

            # Create InfluxDB point
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

            # Add anomaly detection results
            if is_anomaly is not None and reconstruction_error is not None:
                point.tag("predicted_anomaly", "true" if is_anomaly else "false")
                point.field("reconstruction_error", reconstruction_error)

                if is_anomaly:
                    anomaly_count += 1
                else:
                    normal_count += 1

            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

        # Log batch summary
        if anomaly_count > 0 or normal_count > 0:
            print(f"Batch {batch_id}: Written {len(records)} records to InfluxDB")
            print(f"  ✓ Normal: {normal_count}, ⚠ Anomalies: {anomaly_count}")
        else:
            print(f"Batch {batch_id}: Written {len(records)} records to InfluxDB (no anomaly detection)")

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

    # Load anomaly detection models
    models_loaded = load_anomaly_detection_models()
    if not models_loaded:
        print("⚠ WARNING: Continuing without anomaly detection\n")

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