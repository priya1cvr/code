import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.hadoop.fs.{FileSystem, Path}
import scala.math._

object MergeHiveSmallFiles {
  val database = "your_database" // Replace with your Hive DB
  val targetFileSizeMB = 128

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("MergeHiveSmallFiles")
      .enableHiveSupport()
      .getOrCreate()

    import spark.implicits._

    def getTableLocation(table: String): String = {
      val desc = spark.sql(s"DESCRIBE FORMATTED $database.$table")
      desc.filter($"col_name" === "Location").select("data_type").first().getString(0)
    }

    def getTotalSize(pathStr: String): Long = {
      val path = new Path(pathStr)
      val fs = FileSystem.get(spark.sparkContext.hadoopConfiguration)
      fs.listStatus(path)
        .filter(_.isFile)
        .map(_.getLen)
        .sum
    }

    def mergeTable(table: String): Unit = {
      println(s"\nProcessing table: $table")
      val path = getTableLocation(table)
      println(s"Location: $path")
      val totalSizeBytes = getTotalSize(path)
      val partitions = max(1, ceil(totalSizeBytes.toDouble / (targetFileSizeMB * 1024 * 1024)).toInt)
      println(f"Total size: ${totalSizeBytes / (1024.0 * 1024):.2f} MB, Partitions: $partitions")

      val df = spark.table(s"$database.$table")
      df.repartition(partitions).write.mode("overwrite").format("parquet").save(path)
      println(s"✔ Table $table merged and saved with $partitions partitions.")
    }

    if (args.length == 1) {
      mergeTable(args(0))
    } else {
      val tables = spark.sql(s"SHOW TABLES IN $database").select("tableName").as[String].collect()
      tables.foreach(mergeTable)
    }

    spark.stop()
  }
}
