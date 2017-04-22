from mrjob.job import MRJob 
from mrjob.step import MRStep
import re


class SpendByCustSorted(MRJob):
	# if you define steps as step it will give ValueError: Step has no mappers and no reducers
	def steps(self):
		return[
			MRStep(mapper=self.mapper_get_orders,
				   reducer=self.reducer_totals_by_customer),
			MRStep(mapper=self.mapper_make_amount_key,
				   reducer=self.reducer_output_results)
		]
		
	# mapper extracts the key and value we care about ,in this case the key is ignored i.e put as _
	def mapper_get_orders(self,_,line):
 		(custID,itemID,amount)=line.split(',')
		yield custID,float(amount)

 	def reducer_totals_by_customer(self,custID,amount):	
		yield custID,sum(amount)

	def mapper_make_amount_key(self,custID,orderTotal):
		yield '%04.02f'%float(orderTotal),custID	

	def reducer_output_results(self,orderTotal,custIDs):
		for custID in custIDs:
			yield custID,orderTotal

if __name__=='__main__':
	SpendByCustSorted.run()	