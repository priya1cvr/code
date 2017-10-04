

package com.sundogsoftware.sparkstreaming
import org.apache.log4j.Level


object Utilities   {
  /* Make Sure Only Log Messages get Logged to avoid log Spam */
  
  def setupLogging()={
    import org.apache.log4j.{Level,Logger}
   
        
    val rootLogger = Logger.getRootLogger()
    rootLogger.setLevel(Level.ERROR) 
  }
  
  //configure Twitter Service credentials using twitter.txt 
  def setupTwitter() = {
    import scala.io.Source
    
    for (line <-Source.fromFile("/Users/pbishwal/Documents/Techie/SparknScala/scala/SparkStreamingUsingScala/twitter.txt").getLines) {
      val fields =line.split(":") 
      System.setProperty("twitter4j.oauth." + fields(0),fields(1))
    }
  }
  
  
   // Retrives a regex pattern for apache Logs 
  /*
  def apacheLogPattern(): Pattern = {
    val ddd ="\\d(1,3)"
    val ip ="s($ddd\\.$ddd\\.$ddd\\.$ddd)?"
    val client ="(\\S+)"
    val user ="(\\S+)"
    val datetime = "(\\[.+?\\])"
    val request = "\"(.*?)\""
    val status = "(\\d{3})"
    val bytes = "(\\S+)"
    val referrer = "\"(.*?)\""
    val agent = "\"(.*?)\""
  } 
  */
}