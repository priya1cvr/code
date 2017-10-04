

package com.sundogsoftware.sparkstreaming
import org.apache.spark._
import org.apache.spark.SparkContext
import org.apache.spark.streaming._
import org.apache.spark.streaming.twitter._
import org.apache.spark.streaming.{StreamingContext,Seconds}
import org.apache.log4j.Level
import org.apache.spark.streaming.twitter.TwitterUtils
import Utilities._
import twitter4j._

object PrintTweets extends App {
   
  /*Our Main function where action Happens */
  
    
    //configure twitter credentials using twitter.txt 
    setupTwitter()
    
    //setup a Spark Streaming Context named "Print Tweets" that runs locally using all CPU Cores 
    val sparkconf = new SparkConf().setMaster("spark://Priyabrats-MacBook-Air.local:7077").setAppName("Streaming and Batch Join") .set("spark.driver.allowMultipleContexts", "true")
    
    
     val sc = new SparkContext(sparkconf)
     // val ssc = new StreamingContext("local[*]","PrintTweets"  )
     val ssc = new StreamingContext(sc,Seconds(1) ) // here sc should be inside StreamingContext else you get MultipleContext error 

    //Get rid of log spam
    setupLogging()
    
   
    //create a Dstream from Twitter using Spark Streaming Context 
    val tweets = TwitterUtils.createStream(ssc,None)
    
    //Now extract the text of each status update into RDDs using map()
    val statuses =tweets.map(status => status.getText()) 
    
    //print out first ten 
    statuses.print()
    
    //Kick it all off 
    ssc.start()
    ssc.awaitTermination()
    
}