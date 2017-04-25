# This program does a histogram rating of the movies ,how many 5 star ,4 star ...
from pyspark import SparkConf,SparkContext 
import collections 
''' 
SparkContext-Main entry point for Spark functionality,tells Spark how to access a cluster
SparkConf-For configuring Spark.
we create a SparkConf object with SparkConf(), which will load values from spark.*
The appName parameter is a name for your application to show on the cluster UI.
master is a Spark, Mesos or YARN cluster URL, or a special “local” string to run in local mode.
local - means single thread single process 
'''
#set up our context 
conf=SparkConf().setMaster("local").setAppName("RatingsHistorgram")
sc=SparkContext(conf=conf)
#create an rdd called lines which reads from a file 
lines=sc.textFile("/Users/pbishwal/Documents/Techie/SparknScala/SparkCodes/Taming_BigData_WithSpark/ml-100k/u.data")
#textFile -breaks whole file line by line so that each line corresponds to a value in rdd
ratings=lines.map(lambda x:x.split()[2])
# map gives 1 to 1 relation i.e 1 output for 1 input given
# extract 3rd field(starts with 0) userid,movieid,rating,timestamp (u.data file )
result=ratings.countByValue()
#countByValue counts the no. of times rating occurs 
sortedResults=collections.OrderedDict(sorted(result.items()))
#print the result 
for key,value in sortedResults.iteritems():
	print "%s %i" %(key,value)
	
'''
How to invoke this script ??
C:\Users\bishwal\Misc\Hadoop\Spark_Data\Taming_BigData_WithSpark> spark-submit rating_counter.py

spark-submit script allows you to manage your Spark applications. You can submit your
Spark application to a Spark deployment environment, kill or request status of Spark.
When executed, spark-submit script executes org.apache.spark.deploy.SparkSubmit class.

output of the script : 
1 6110
2 11370
3 27145
4 34174
5 21201
'''	