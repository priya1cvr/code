import java.util.Properties

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.SaveMode

// Importing the SparkSession gives access to all the SQL functions and implicit conversions.
import spark.implicits._
val spark = SparkSession.builder().appName("RDD Relation").config("spark.some.config.option", "some-value").getOrCreate()

case class Record(Key:Int,Value:String) 

val df =spark.createDataFrame((1 to 100).map(i=>Record(i,s"val_$i")))
df.createOrReplaceTempView("records")

// Once tables have been registered, you can run SQL queries over them.
println("Result of SELECT *:")

spark.sql("SELECT * FROM records").collect().foreach(println)

val count =spark.sql("SELECT count(*) FROM records").collect().head.getLong(0)
res7: Long = 100

println(s"COUNT(*): $count")
COUNT(*): 100

// The results of SQL queries are themselves RDDs and support all normal RDD functions. The
// items in the RDD are of type Row, which allows you to access each column by ordinal.

val rddFromSql= spark.sql("SELECT * FROM records where key between 10 and 20 ")
rddFromSql.show()

println("Result of RDD.map:")
rddFromSql.rdd.map(row=>s"key:${row(0)} ,Value:${row(1)}").collect().foreach(println)

// Queries can also be written using a LINQ-like Scala DSL.
df.where($"key"===1).orderBy($"value".asc).select($"key").collect.foreach(println)

// Write out an RDD as a parquet file with overwrite mode.
df.write.mode(SaveMode.Overwrite).parquet("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/pair/pair.parquet")

 // Read in parquet file.  Parquet files are self-describing so the schema is preserved.
 spark.read.load("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/pair/pair.parquet/part-00000.parquet").show()
 
 OR 
 val parquetFile = spark.read.parquet("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/pair/pair.parquet/part-00000.parquet")
 
  // Queries can be run using the DSL on parquet files just like the original RDD.
scala>   parquetFile.where($"key"===2).select($"value".as("a")).collect().foreach(println)
[val_2]
  
  
 // These files can also be used to create a temporary view.
  parquetFile.createOrReplaceTempView("parquetFile")
  spark.sql("SELECT * FROM parquetFile").collect().foreach(println)
  [1,val_1]
  [2,val_2]
  ...
  ...
  
   
  
  
 