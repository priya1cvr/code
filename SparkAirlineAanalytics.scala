start spark shell to include csv packages from bin folder 
./spark-shell --master "local[*]" --packages com.databricks:spark-csv_2.10:1.0.3 

val sqlContext = new org.apache.spark.sql.SQLContext(sc)
import sqlContext.implicits._ 


val airportDF =sqlContext.load("com.databricks.spark.csv",Map("path" -> "/Users/p.kumar.bishwal/Documents/python/codeNdata/airport.csv" ,"header" -> "true"))
The load operation will parse the *.csv file using Databricks spark-csv library and return a dataframe with column names same as in the first header line in file.

if creating the above DF creates error i.e unable to connect  then you can use below DFs

#val src = scala.io.Source.fromFile("/Users/p.kumar.bishwal/Documents/python/codeNdata/airport.csv").getLines

====file layout
AirportID,Name,City,Country,FAA,ICAO,Latitude,Longitude,Altitude,Timezone,DST,Tz
1,"Goroka","Goroka","Papua New Guinea","GKA","AYGA",-6.081689,145.391881,5282,10,"U","Pacific/Port_Moresby"
======


case class Airport(AirportID: Int, Name: String, City: String, Country: String, FAA: String,ICAO: String ,Latitude : Double,Longitude: Double ,Altitude: Int,Timezone: Double,DST: String,Tz: String)

val header=sc.textFile("/Users/p.kumar.bishwal/Documents/python/codeNdata/airport.csv").first()
#remove header aand 
val airportDF = sc.textFile("/Users/p.kumar.bishwal/Documents/python/codeNdata/airport.csv").filter(x => x != header).map(_.split(",")).map(p => Airport(p(0).trim.toInt, p(1).trim, p(2).trim, p(3).trim, p(4).trim, p(5).trim, p(6).toDouble, p(7).toDouble, p(8).toInt, p(9).toDouble, p(10), p(11))).toDF()

airportDF.registerTempTable("airports")

if using the case class to create df then Latitude<0.0 else if use sqlContext to create df then use Latitude<0 ..
sqlContext.sql("select AirportID, Name, Latitude, Longitude from airports where Latitude<0.0 and Longitude>0.0").collect().foreach(println)
[1,"Goroka",-6.081689,145.391881]
[2,"Madang",-5.207083,145.7887]
[3,"Mount Hagen",-5.826789,144.295861]
[4,"Nadzab",-6.569828,146.726242]
[5,"Port Moresby Jacksons Intl",-9.443383,147.22005]
[6,"Wewak Intl",-3.583828,143.669186]

Q.find out how many unique cities have airports in each country ?

sqlContext.sql("select Country, count(distinct(City)) from airports group by Country").collect.foreach(println)
[Iceland,10]                                                                    
[Canada,131]
[Greenland,4]
[Papua New Guinea,6]

Q. What is average Altitude (in feet) of airports in each Country?
sqlContext.sql("select Country , avg(Altitude) from airports group by Country").collect

[Iceland,72.8]
[Canada,852.6666666666666]
[Greenland,202.75]
[Papua New Guinea,1849.0]

Q.find out in each timezones how many airports are operating?

scala> sqlContext.sql("select Tz , count(Tz) from airports group by Tz").collect.foreach(println)
[Atlantic/Reykjavik,10]
[America/Vancouver,19]
[America/Toronto,48]
[America/Coral_Harbour,3]
[America/Halifax,9]
[America/Edmonton,27]
[America/Godthab,3]
[America/Regina,10]
[America/Thule,1]
[America/Dawson_Creek,1]
[America/St_Johns,4]
[Pacific/Port_Moresby,6]
[America/Winnipeg,14]


Q. calculate average latitude and longitude for these airports in each country

[Iceland,65.0477736,-19.5969224]
[Canada,53.94868565185185,-93.95003623703704]
[Greenland,67.22490275,-54.124131999999996]
[Papua New Guinea,-6.118766666666666,145.51532]

Q. count how many different DSTs are there
scala> sqlContext.sql("select count(distinct(DST)) from airports").collect.foreach(println)
[4]

###Saving data in CSV format Till now we loaded and queried csv data. Now we will see how to save results in CSV format back to filesystem.
 Suppose we want to send report to client about all airports in northwest part of all countries. 
Lets calculate that first.

val NorthWestAirportsDF=sqlContext.sql("select AirportID, Name, Latitude, Longitude from airports where Latitude>0 and Longitude<0")

And save it to CSV file
NorthWestAirportsDF.save("com.databricks.spark.csv", org.apache.spark.sql.SaveMode.ErrorIfExists, Map("path" -> "/Users/p.kumar.bishwal/Documents/python/codeNdata/output/NorthWestAirports.csv","header"->"true"))

The following are the parameters passed to save method.
    Source: it same as load method com.databricks.spark.csv which tells spark to save data as csv.
    SaveMode: This allows user to specify in advance what needs to be done if the given output path already exists. 
    		  So that existing data wont get lost/overwritten by mistake. You can throw error, append or overwrite. 
    		  Here, we have thrown an error ErrorIfExists as we dont want to overwrite any existing file.
    Options: These options are same as what we passed to load method. Options:

