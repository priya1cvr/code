from mrjob.job import MRJob 

class MRMinMTemp(MRJob):

	def MakeFahrenheit(self,tenthOfCelcius):
		celsius =float(tenthOfCelcius)/10.0
		fahrenheit=celsius*1.8+32
		return fahrenheit
	# mapper extracts the key and value we care about  ,in this case the key is ignored i.e put as _
	def mapper(self,_,line):
		(location,date,type,data,x,y,z,w)=line.split(',')
		if (type=="TMIN"):
			temperature=self.MakeFahrenheit(data)
			yield location,temperature # here temperature is a list of temp's for the given location 

	# reducer is called for each location
	def reducer(self,location,temperature):	
		yield location,min(temperature)

if __name__=='__main__':
	MRMinMTemp.run()			
