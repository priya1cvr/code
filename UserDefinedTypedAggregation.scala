import java.util.Properties

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.SaveMode
import org.apache.spark.sql.{Encoder, Encoders, SparkSession}
import org.apache.spark.sql.expressions.Aggregator

// Importing the SparkSession gives access to all the SQL functions and implicit conversions.
import spark.implicits._
val spark = SparkSession.builder().appName("User Defined Type aggr").config("spark.some.config.option", "some-value").getOrCreate()

case class Employee(name:String,salary:Long)
case class Average(var sum:Long, var count:Long) 

val ds =spark.read.json("/Users/p.kumar.bishwal/Documents/python/codeNdata/employees.json").as[Employee]  // here Employee is case class
scala> ds.show()
+-------+------+
|   name|salary|
+-------+------+
|Michael|  3000|
|   Andy|  4500|
| Justin|  3500|
|  Berta|  4000|
+-------+------+



object MyAverage extends Aggregator[Employee ,Average,Double{
	def zero:Average = Average(0L,0L)
	def reduce(buffer:Average,employee:Employee): Average = {
		buffer.sum +=employee.salary
		buffer.count+=1
		buffer 
	}	
 def merge(b1:Average,b2:Average): Average = {
 	b1.sum+=b2.sum
 	b1.count+=b2.count
 	b1
 }
 
 def finish(reduction:Average):Double =reduction.sum.toDouble/reduction.count 

 def bufferEncoder:Encoder[Average] = Encoders.product 
 
 def outputEncoder:Encoder[Double] =Encoders.scalaDouble 
	
}



 // Convert the function to a `TypedColumn` and give it a name
 val averageSalary = MyAverage.toColumn.name("average_salary") 
 val result = ds.select(averageSalary)
 
 result.show()