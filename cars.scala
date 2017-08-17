val rawData=sc.textFile("/Users/p.kumar.bishwal/Documents/python/codeNdata/cars.txt")

# map columns and datatypes
case class cars(make:String, model:String, mpg:Integer, cylinders :Integer, engine_disp:Integer, horsepower:Integer, weight:Integer ,accelerate:Double,	year:Integer, origin:String)

val carsData =rawData.map(x=>x.split(",")).map(x=>cars(x(0).toString,x(1).toString,x(2).toInt,x(3).toInt,x(4).toInt,x(5).toInt,x(6).toInt,
x(7).toDouble,x(8).toInt,x(9).toString))

#persist to memory
carsData.cache()

#count cars origin wise
scala> carsData.map(x=>(x.origin,1)).reduceByKey((x,y)=>x+y).collect()
res27: Array[(String, Int)] = Array((American,47), (European,9), (Japanese,6))

#filter out american cars
val americanCars=carsData.filter(x=>(x.origin=="American"))

#count total american cars
americanCars.count()
res29: Long = 47

#take sum of weights according to make
myapproach:
find the weighted average so took the sum and then the count to find avg 

americanCars.map(x=>(x.make,x.weight.toInt)).mapValues(x=>(x,1)).reduceByKey((x,y)=>(x._1 + y._1,x._2 + y._2)).
mapValues(x => 1.0 * x._1 / x._2).collect()

lets break the above step by step:
americanCars.map(x=>(x.make,x.weight.toInt)).collect
res79: Array[(String, Int)] = Array((amc,3850), (amc,2648), (amc,2774), (amc,3433), (buick,3086), (buick,3693), (chevrolet,3504), (chevrolet,4354), (chevrolet,3761), (chevy,4376), (dodge,3563), (dodge,4382), (ford,4615), (ford,4341), (ford,2587), (ford,3449), (hi,4732), (plymouth,3609), (plymouth,2833), (plymouth,4312), (plymouth,3436), (pontiac,4425), (amc,2634), (amc,2962), (amc,3288), (chevrolet,3329), (chevrolet,4209), (chevrolet,2408), (chevrolet,2264), (dodge,4955), (ford,4746), (ford,4154), (ford,3139), (ford,3302), (mercury,2220), (plymouth,1955), (plymouth,4096), (plymouth,3439), (pontiac,4464), (pontiac,3282), (pontiac,5140), (amc,3672), (amc,3892), (buick,4502), (chevrolet,4098), (chevrolet,4274), (chevrolet,2408))

americanCars.map(x=>(x.make,x.weight.toInt)).mapValues(x=>(x,1)).collect
res80: Array[(String, (Int, Int))] = Array((amc,(3850,1)), (amc,(2648,1)), (amc,(2774,1)), (amc,(3433,1)), (buick,(3086,1)), (buick,(3693,1)), (chevrolet,(3504,1)), (chevrolet,(4354,1)), (chevrolet,(3761,1)), (chevy,(4376,1)), (dodge,(3563,1)), (dodge,(4382,1)), (ford,(4615,1)), (ford,(4341,1)), (ford,(2587,1)), (ford,(3449,1)), (hi,(4732,1)), (plymouth,(3609,1)), (plymouth,(2833,1)), (plymouth,(4312,1)), (plymouth,(3436,1)), (pontiac,(4425,1)), (amc,(2634,1)), (amc,(2962,1)), (amc,(3288,1)), (chevrolet,(3329,1)), (chevrolet,(4209,1)), (chevrolet,(2408,1)), (chevrolet,(2264,1)), (dodge,(4955,1)), (ford,(4746,1)), (ford,(4154,1)), (ford,(3139,1)), (ford,(3302,1)), (mercury,(2220,1)), (plymouth,(1955,1)), (plymouth,(4096,1)), (plymouth,(3439,1)), (pontiac,(4464,1)), (pontiac,(3282,1))

americanCars.map(x=>(x.make,x.weight.toInt)).mapValues(x=>(x,1)).reduceByKey((x,y)=>(x._1 + y._1,x._2 + y._2)).collect
res81: Array[(String, (Int, Int))] = Array((chevrolet,(34609,10)), (plymouth,(23680,7)), (buick,(11281,3)), (pontiac,(17311,4)), (hi,(4732,1)), (chevy,(4376,1)), (mercury,(2220,1)), (amc,(29153,9)), (dodge,(12900,3)), (ford,(30333,8)))

res83: Array[(String, Double)] = Array((chevrolet,3460.9), (plymouth,3382.8571428571427), (buick,3760.3333333333335), (pontiac,4327.75), (hi,4732.0), (chevy,4376.0), (mercury,2220.0), (amc,3239.222222222222), (dodge,4300.0), (ford,3791.625))

other approach:
================
#take sum of weights according to make
val makeWeightSum = americanCars.map(x=>(x.make,x.weight.toInt)).combineByKey((x:Int)=>(x,1),
(acc:(Int,Int),x)=>(acc._1+x,acc._2+1) , 
(acc1:(Int,Int),acc2:(Int,Int))=>(acc1._1 + acc2._1,acc1._2 + acc2._2) ) 

res36: Array[(String, (Int, Int))] = Array((chevrolet,(34609,10)), (plymouth,(23680,7)), (buick,(11281,3)), (pontiac,(17311,4)), (hi,(4732,1)), (chevy,(4376,1)), (mercury,(2220,1)), (amc,(29153,9)), (dodge,(12900,3)), (ford,(30333,8)))


#take average
val makeWeightAvg = makeWeightSum.map(x=>(x._1, (1.0 *x._2._1/x._2._2)))

1.0 is multiplied to convert into double 
makeWeightAvg.collect()
res84: Array[(String, Double)] = Array((chevrolet,3460.9), (plymouth,3382.8571428571427), (buick,3760.3333333333335), (pontiac,4327.75), (hi,4732.0), (chevy,4376.0), (mercury,2220.0), (amc,3239.222222222222), (dodge,4300.0), (ford,3791.625))
