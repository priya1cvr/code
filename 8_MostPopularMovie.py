from mrjob.job import MRJob 
from mrjob.step import MRStep

class MostPopularMovie(MRJob):

	def steps(self):
		return[
			MRStep(mapper=self.mapper_get_ratings,
				   reducer=self.reducer_count_ratings),
			MRStep(reducer=self.reducer_find_max)
		]
	# mapper extracts the key and value we care about ,here key is rating and value is its occurence 
	def mapper_get_ratings(self,_,line):
		(userID,movieID,rating,timestamp)=line.split('\t')
		yield movieID,1

	def reducer_count_ratings(self,key,values):
		yield None,(sum(values),key)

	# to this reducer every key has value none and values are like [(300,241) ,(124,782),(534,50)] .... where 1st part is # of occurence of the movie and 2nd part is movieID
	def reducer_find_max(self,key,values):
		yield max(values)


if __name__=='__main__':
	MostPopularMovie.run()			


''' input to 2nd reducer is like below :
values=[(300,241) ,(124,782),(534,50)] i.e it is a list of tuples 
o/p is 
max(values) max of values always take the 1st argument in a tuple to perform max 
(534, 50)
'''