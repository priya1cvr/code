import org.apache.hadoop.fs.{FileSystem, Path}
import org.apache.spark.sql.SparkSession

def getSizeInMB(path: String, spark: SparkSession): Long = {
  val fs = FileSystem.get(spark.sparkContext.hadoopConfiguration)
  val size = fs.getContentSummary(new Path(path)).getLength
  size / (1024 * 1024)
}

val partitionPath = "hdfs:///data/table/reporting_date=20240517/country_code=US"
val sizeInMB = getSizeInMB(partitionPath, spark)

// Estimate number of files to write
val targetFileSizeMB = 128
val numFiles = Math.ceil(sizeInMB.toDouble / targetFileSizeMB).toInt

df.coalesce(numFiles).write.partitionBy("reporting_date", "country_code").parquet(partitionPath)

=================

val targetFileSizeMB = 128

val dates = df.select("date").distinct().as[String].collect()

dates.foreach { date =>
  val dfForDate = df.filter(col("date") === date)

  // Estimate number of files
  val estSizeInMB = dfForDate.rdd.map(_.toString().getBytes.length).sum() / (1024 * 1024)
  val numFiles = math.max(1, (estSizeInMB / targetFileSizeMB).toInt)

  dfForDate
    .coalesce(numFiles)
    .write
    .mode("append")
    .parquet(s"/output/path/date=$date")
}

=================
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.files.maxPartitionBytes", 134217728) // 128MB

import spark.implicits._

// Simulated data
val df = (1 to 1000000).toDF("id")
  .withColumn("date", expr("concat('2024-05-', lpad(cast((id % 20 + 1) as string), 2, '0'))"))
  .withColumn("value", rand())

// Coalesce and partition by date
df.coalesce(10)
  .write
  .mode("overwrite")
  .partitionBy("date")
  .parquet("/tmp/test-output")
