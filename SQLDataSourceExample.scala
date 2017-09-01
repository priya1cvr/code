import java.util.Properties

import org.apache.spark.sql.SparkSession


val spark = SparkSession.builder().appName("Spark SQL data sources example").config("spark.some.config.option", "some-value").getOrCreate()

#reading a parquet file 
val usersDF = spark.read.load("/Users/p.kumar.bishwal/Documents/python/codeNdata/users.parquet")
scala> usersDF.show()
+------+--------------+----------------+
|  name|favorite_color|favorite_numbers|
+------+--------------+----------------+
|Alyssa|          null|  [3, 9, 15, 20]|
|   Ben|           red|              []|
+------+--------------+----------------+

scala> usersDF.select("name","favorite_color").show()
+------+--------------+
|  name|favorite_color|
+------+--------------+
|Alyssa|          null|
|   Ben|           red|
+------+--------------+

# write and save into a parquet file 
usersDF.select("name","favorite_color").write.save("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/output/namesAndFavColors.parquet") 

this will create a folder namesAndFavColors in the directory specified and data will be inside part-0000 file 
you can read the parquet file saved again as below : 
scala> spark.read.load("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/namesAndFavColors.parquet/part-00000-f44495e1-5b4d-4583-9d8d-4a46b347f1d7-c000.snappy.parquet").show()
+------+--------------+
|  name|favorite_color|
+------+--------------+
|Alyssa|          null|
|   Ben|           red|
+------+--------------+

# read a json file and save from json data to parquet 
val personsDF = spark.read.format("json").load("/Users/p.kumar.bishwal/Documents/python/codeNdata/people.json")

scala> personsDF.show()
+----+-------+
| age|   name|
+----+-------+
|null|Michael|
|  30|   Andy|
|  19| Justin|
+----+-------+


#save from json data to parquet 

personsDF.write.save("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/peoples.parquet")
now you can see the peoples.parquet folder in the location provided 

# now read from above parquet file 
scala> spark.read.load("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/peoples.parquet/part-00000-b0116105-a558-404b-8dc8-149bf877f4ea-c000.snappy.parquet").show()
+----+-------+
| age|   name|
+----+-------+
|null|Michael|
|  30|   Andy|
|  19| Justin|
+----+-------+


# directly query the parquet file 
val sqlDF = spark.sql("SELECT * FROM parquet.`/Users/p.kumar.bishwal/Documents/python/codeNdata/output/peoples.parquet/part-00000-b0116105-a558-404b-8dc8-149bf877f4ea-c000.snappy.parquet`")
 
 
 scala> sqlDF.show()
+----+-------+
| age|   name|
+----+-------+
|null|Michael|
|  30|   Andy|
|  19| Justin|
+----+-------+



For file-based data source, it is also possible to bucket and sort or partition the output. Bucketing and sorting are applicable only to persistent tables:

personsDF.write.bucketBy(42,"name").sortBy("age").saveAsTable("people_bucketed") 

Buckets the output by the given columns. If specified, the output is laid out on the file system similar to Hive's bucketing scheme. 

scala>  spark.sql("SELECT * FROM people_bucketed").show()
+----+-------+
| age|   name|
+----+-------+
|null|Michael|
|  30|   Andy|
|  19| Justin|
+----+-------+


if you see the table structure it will be clustered by name into 42 buckets as we create the hive table 
since the dataframe is parquet file the table created is also parquet format 


scala> spark.sql("show create table people_bucketed").collect.foreach(println)
[CREATE TABLE `people_bucketed` (`age` BIGINT, `name` STRING)
USING parquet
OPTIONS (`serialization.format` '1')
CLUSTERED BY (name) SORTED BY (age) INTO 42 BUCKETS ]

#partiton usersDF by color 
usersDF.write.partitionBy("favorite_color").format("parquet").save("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/namesPartByColor.parquet")


scala> spark.read.load("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/namesAndFavColors.parquet/part-00000.snappy.parquet").show()
+------+--------------+
|  name|favorite_color|
+------+--------------+
|Alyssa|          null|
|   Ben|           red|
+------+--------------+

# save as table partition by color 
usersDF.write.partitionBy("favorite_color").saveAsTable("users_partition") 

scala> spark.sql("show create table users_partition").collect.foreach(println)
[CREATE TABLE `users_partition` (`name` STRING, `favorite_numbers` ARRAY<INT>, `favorite_color` STRING)
USING parquet OPTIONS ( `serialization.format` '1') PARTITIONED BY (favorite_color)
]


# read from parquet file and store it in csv file 

# val usersDF = spark.read.load("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/users.parquet")
this is done above 


note since usersDF contains array datatype we are unable to save it directly to CSV 
scala> usersDF.write.format("csv").option("header", "true").save("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/users.csv")
java.lang.UnsupportedOperationException: CSV data source does not support array<int> data type.
  at org.apache.spark.sql.execution.datasources.csv.CSVUtils$.org$apache$spark$sql$execution$datasources$csv$CSVUtils$$verifyType$1(CSVUtils.scala:127)

so , we are using personsDF 
#val personsDF = spark.read.format("json").load("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/people.json")

personsDF.write.format("csv").option("header", "true").save("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/users.csv")


# reading from csv file 
val src = scala.io.Source.fromFile("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/users.csv/part-00000.csv").getLines
for (line <- src) {
        val cols = line.split(",").map(_.trim)
        println(s"${cols(0)}|${cols(1)}")
    }

age|name
|Michael
30|Andy
19|Justin

// $example off:write_partitioning$
    // $example on:write_partition_and_bucket$

# another method to save parquet file 
personsDF.write.parquet("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/persons.parquet")

// The result of loading a Parquet file is also a DataFrame
val parquetFileDF=spark.read.parquet("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/persons.parquet/part-00000.parquet") 
scala> parquetFileDF.show()
+----+-------+
| age|   name|
+----+-------+
|null|Michael|
|  30|   Andy|
|  19| Justin|
+----+-------+

parquetFileDF.createOrReplaceTempView("parquetFile") 
val namesDF = spark.sql("SELECT name FROM parquetFile WHERE age BETWEEN 13 AND 19")
scala> namesDF.map(attributes => "Name: " + attributes(0)).show()
+------------+
|       value|
+------------+
|Name: Justin|
+------------+

=======================
import spark.implicits._

// Create a simple DataFrame, store into a partition directory
val squaresDF =spark.sparkContext.makeRDD(1 to 5).map(i=>(i,i*i)).toDF("value","square")
squaresDF.write.parquet("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/test_table/key=1")

now you can read the file in 3 ways 

1st 
scala> spark.read.parquet("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/test_table/key=1/part-00000.parquet").show()
+-----+------+
|value|square|
+-----+------+
|    1|     1|
+-----+------+

2nd
scala> spark.read.load("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/test_table/key=1/part-00001.parquet").show()

+-----+------+
|value|square|
+-----+------+
|    2|     4|
+-----+------+

3rd
spark.sql("SELECT * FROM parquet.`/Users/p.kumar.bishwal/Documents/python/codeNdata/output/test_table/key=1/part-00002.parquet`").show()
17/08/23 17:10:46 WARN ObjectStore: Failed to get database parquet, returning NoSuchObjectException
+-----+------+
|value|square|
+-----+------+
|    3|    9|
+-----+------+

// Create another DataFrame in a new partition directory,
// adding a new column and dropping an existing column

val cubesDF =spark.sparkContext.makeRDD(1 to 5).map(i=>(i,i*i*i)).toDF("value","cube")
cubesDF.write.parquet("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/test_table/key=2")


 // Read the partitioned table
 val mergedDF =spark.read.option("mergeSchema" , "true").parquet("/Users/p.kumar.bishwal/Documents/python/codeNdata/output/test_table")
 mergedDF.printSchema()
 root
 |-- value: integer (nullable = true)
 |-- square: integer (nullable = true)
 |-- key: integer (nullable = true)


// Alternatively, a DataFrame can be created for a JSON dataset represented by
// a Dataset[String] storing one JSON object per string

val otherPeopleDataset = spark.createDataset("""{"name":"Yin","address":{"city":"Columbus","state":"Ohio"}}""" :: Nil)
scala> otherPeopleDataset.collect()
res83: Array[String] = Array({"name":"Yin","address":{"city":"Columbus","state":"Ohio"}})


val otherPeople =spark.read.json(otherPeopleDataset)

there are 2 ways to read from DF
1st 
scala> otherPeople.show()
+---------------+----+
|        address|name|
+---------------+----+
|[Columbus,Ohio]| Yin|
+---------------+----+

2nd
scala> otherPeople.select("address").show()
+---------------+
|        address|
+---------------+
|[Columbus,Ohio]|
+---------------+


scala> val conf = new SparkConf().setMaster("local[2]").setAppName("NetworkWordCount").set("spark.driver.allowMultipleContexts", "true")
conf: org.apache.spark.SparkConf = org.apache.spark.SparkConf@531bfe4b

scala> val ssc = new StreamingContext(sc, Seconds(2) )
