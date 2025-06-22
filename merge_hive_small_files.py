from pyspark.sql import SparkSession
import sys
import math
from py4j.java_gateway import java_import

# --- Configuration ---
DATABASE = "your_database"  # replace with actual Hive DB
TARGET_FILE_SIZE_MB = 128

# --- Initialize SparkSession ---
spark = SparkSession.builder \
    .appName("MergeHiveSmallFiles") \
    .enableHiveSupport() \
    .getOrCreate()

sc = spark.sparkContext
java_import(sc._jvm, 'org.apache.hadoop.fs.*')
hadoop_conf = sc._jsc.hadoopConfiguration()
fs = sc._jvm.FileSystem.get(hadoop_conf)

def get_table_location(database, table):
    desc_df = spark.sql(f"DESCRIBE FORMATTED {database}.{table}")
    location = desc_df.filter("col_name='Location'").select("data_type").first()[0]
    return location

def get_total_size_bytes(path):
    total_size = 0
    status = fs.listStatus(Path(path))
    for file in status:
        if file.isFile():
            total_size += file.getLen()
    return total_size

def merge_table(database, table):
    print(f"\nProcessing table: {table}")
    location = get_table_location(database, table)
    print(f"Location: {location}")

    total_size_bytes = get_total_size_bytes(location)
    target_file_size_bytes = TARGET_FILE_SIZE_MB * 1024 * 1024
    partitions = max(1, math.ceil(total_size_bytes / target_file_size_bytes))
    print(f"Total size: {total_size_bytes / (1024 * 1024):.2f} MB, Target partitions: {partitions}")

    df = spark.table(f"{database}.{table}")
    df.repartition(partitions).write.mode("overwrite").format("parquet").save(location)
    print(f"✔ Table {table} merged and saved with {partitions} partitions.")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        merge_table(DATABASE, sys.argv[1])
    else:
        tables = spark.sql(f"SHOW TABLES IN {DATABASE}").select("tableName").rdd.flatMap(lambda x: x).collect()
        for table in tables:
            merge_table(DATABASE, table)
