from mrjob.job import MRJob 

class SpendByCust(MRJob):

	# mapper extracts the key and value we care about  ,in this case the key is ignored i.e put as _
	def mapper(self,_,line):
		(custID,itemID,amount)=line.split(',')
		yield custID,float(amount) 
		# here amount is a list of amount's for the given customer 

	# reducer is called for each location
	def reducer(self,custID,amount):	
		yield custID,sum(amount)

if __name__=='__main__':
	SpendByCust.run()			
