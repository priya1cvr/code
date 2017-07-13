reference:https://github.com/sameeraxiomine/sparkusingjava8/blob/master/src/main/java/com/axiomine/spark/examples/airline/datagen/AirlineDataSampler.java


package org.airline;
import java.io.File;
import java.io.Serializable;
import java.util.Collection;
import java.util.Comparator;

import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.spark.Partitioner;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;

import scala.Tuple2;

public class AirlineDataSampler {
	public static class CustomPartitioner extends Partitioner implements Serializable {
		private static final long serialVersionUID=1L;
		private int partitions;
		public CustomPartitioner(int noOfPartitioners){
			partitions=noOfPartitioners; 
			}
		@Override
		public int getPartition(Object key) {
			String [] sa = StringUtils.splitPreserveAllTokens(key.toString(),',');
			//System.out.println(sa);
			int y=(Integer.parseInt(sa[0])-1987);
			System.out.println(y);
			return (y%partitions);
		}

		@Override
		public int numPartitions() {
			return partitions;
		}
		
	}
	
	public static class CustomCompartor implements Comparator,Serializable{
		private static final long serialVersionUID=1L;
		
		@Override
		public int compare(Object o1, Object o2) {
			String s1 =(String) o1;
			String s2 =(String) o2;
			String [] p1 =StringUtils.splitPreserveAllTokens(s1,',');
			String [] p2 =StringUtils.splitPreserveAllTokens(s2,',');
			
			Integer y1 = Integer.parseInt(p1[0]);
			Integer y2 =Integer.parseInt(p2[0]);
			System.out.println("y1 : "+y1+"y2 : "+y2);
			int result = y1.compareTo(y2);
			
			if(result==0) {
				Integer m1 =Integer.parseInt(p1[1]);
				Integer m2 =Integer.parseInt(p2[1]);
				System.out.println("m1 : "+m1+"m2 : "+m2);
				result= m1.compareTo(m2);
			}
			if(result==0) {
				Integer d1 =Integer.parseInt(p1[2]);
				Integer d2 =Integer.parseInt(p2[2]);
				System.out.println("d1 : "+d1+"d2 : "+d2);
				result= d1.compareTo(d2);
			}
			return result;
		}
		
	}
	@SuppressWarnings({ "resource", "unchecked" })
	public static void main (String args[]) throws Exception {
		String inputPath=args[0];
		String outputPath=args[1];
		float sampledAmount=Float.parseFloat(args[2]);
		
		/*Identify the original number of partitions*/
		String[] extensions = {"csv"}; 
		Collection <File> files =FileUtils.listFiles(new File(inputPath),extensions, false);
		int noOfPartitions = 2;//files.size();
		
		/*Delete output file. Do not do this in Production*/	
		FileUtils.deleteQuietly(new File(outputPath));
		
		/*Initialize Spark Context*/
		JavaSparkContext sc = new JavaSparkContext("local","airlinedatasampler");
		
		/*Read in the data*/
		JavaRDD <String> rdd =sc.textFile(inputPath);
		
		/* Process the data all in a single statement 
		 
		rdd.filter(l->!(l.startsWith("Year"))) //skip the header line
				//.sample(false,sampledAmount)
			     //.repartition(20)
				 .mapToPair(l->{
					 String [] parts =StringUtils.splitPreserveAllTokens(l,",");
					 String yrMoDd =	parts[0]+","+parts[1]+","+parts[2];
					 return new Tuple2<String,String>(yrMoDd,l);
				 })
				 .repartitionAndSortWithinPartitions(
						 new CustomPartitioner(noOfPartitions),
						 new CustomCompartor()
						 )
				 .map(t->((Tuple2<String, String>) t)._2()) //process just the value the 2nd part 
				 .saveAsTextFile(outputPath);
		
		//mapToPair will return the combination of year-Mon-Day as key and rest string as value
		
		*/
		
		/* Process the data divided into rdd's */
		
		JavaPairRDD<String, String> rdd1 =rdd.filter(l->!(l.startsWith("Year")))
								.mapToPair(l->{
									 String [] parts =StringUtils.splitPreserveAllTokens(l,",");
									 String yrMoDd =	parts[0]+","+parts[1]+","+parts[2];
									 return new Tuple2<String,String>(yrMoDd,l);
								 });
		//System.out.println(rdd1.collect());
		
		/* rdd1 gives list of key,value pair as return type is String,String . 
		   mapToPair will return the combination of year-Mon-Day as key and rest string as value
		[(1987,10,14,1987,10,14,3,741,730,912,849,PS,1451,NA,91,79,NA,23,11,SAN,SFO,447,
			NA,NA,0,NA,0,NA,NA,NA,NA,NA), () ...]
		*/
		JavaPairRDD<String, String> rdd2 =rdd1.repartitionAndSortWithinPartitions(
				 new CustomPartitioner(noOfPartitions),
				 new CustomCompartor()
				 );
		//rdd2 also gives same result as rdd1 but the records are sorted 
		
		JavaRDD<Object> rdd3=rdd2.map(t->((Tuple2<String, String>) t)._2());
		
		System.out.println(rdd3.collect());
		//rdd3 gives the key value pair same as rdd2
			sc.close();
	}
}

