from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# -----------------------
# 1️⃣ Create Spark Session
# -----------------------
spark = SparkSession.builder \
    .appName("IoMT Kafka Spark Consumer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# -----------------------
# 2️⃣ Define Schema
# -----------------------
schema = StructType([
    StructField("Header_Length", DoubleType(), True),
    StructField("Protocol Type", StringType(), True),
    StructField("Time_To_Live", DoubleType(), True),
    StructField("Rate", DoubleType(), True),
    StructField("fin_flag_number", DoubleType(), True),
    StructField("syn_flag_number", DoubleType(), True),
    StructField("rst_flag_number", DoubleType(), True),
    StructField("psh_flag_number", DoubleType(), True),
    StructField("ack_flag_number", DoubleType(), True),
    StructField("ece_flag_number", DoubleType(), True),
    StructField("cwr_flag_number", DoubleType(), True),
    StructField("ack_count", DoubleType(), True),
    StructField("syn_count", DoubleType(), True),
    StructField("fin_count", DoubleType(), True),
    StructField("rst_count", DoubleType(), True),
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
    StructField("Number", DoubleType(), True),
    StructField("Variance", DoubleType(), True),
    StructField("Label", StringType(), True)
])

# -----------------------
# 3️⃣ Read Kafka Stream
# -----------------------
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "iomt_traffic_stream") \
    .option("startingOffsets", "latest") \
    .load()

# Convert bytes to string
raw_df = kafka_df.selectExpr("CAST(value AS STRING)")

# Parse JSON to structured columns
json_df = raw_df.select(from_json(col("value"), schema).alias("data")).select("data.*")

# -----------------------
# 4️⃣ Real-time Preprocessing
# -----------------------
preprocessed_df = json_df.withColumn("Header_Length_norm", col("Header_Length") / 1500) \
                         .withColumn("Rate_norm", col("Rate") / 1000) \
                         .withColumn("Time_To_Live_norm", col("Time_To_Live") / 255)

# -----------------------
# 5️⃣ ML Prediction Placeholder
# -----------------------
def predict_batch(df, epoch_id):
    pandas_df = df.toPandas()
    # TODO: Replace with your ML model
    # Example: predictions = model.predict(pandas_df[feature_columns])
    print(f"Batch {epoch_id} prediction preview:")
    print(pandas_df.head())

# -----------------------
# 6️⃣ Start Streaming Query
# -----------------------
query = preprocessed_df.writeStream \
    .foreachBatch(predict_batch) \
    .outputMode("append") \
    .start()

query.awaitTermination()
