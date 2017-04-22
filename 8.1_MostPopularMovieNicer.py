'''Most Popular movie gave the most watched movie ID but we want to know the name of that movieID'''

import sys
 
from mrjob.job import MRJob 
from mrjob.step import MRStep

class MostPopularMovie(MRJob):

	def configure_options(self):
		super(MostPopularMovie,self).configure_options()
		self.add_file_option('--items',help='Path to u.item')
		# add_file_option means we want to send another aniclliary file i.e u.item which keeps the movieID and movieNames
		# when we pass it as a parmeter after --items that file assuming its found will be distributed along wiht the script to every node of the cluster 
		

	def steps(self):
		return[
			MRStep(mapper=self.mapper_get_ratings,
				   reducer_init=self.reducer_init,
				   reducer=self.reducer_count_ratings) ,
			MRStep(reducer=self.reducer_find_max)
		]
	# mapper extracts the key and value we care about ,here key is movieID and value is its occurence i/p to mapper is u.data
	def mapper_get_ratings(self,_,line):
		(userID,movieID,rating,timestamp)=line.split('\t')
		yield movieID,1

	def reducer_init(self):
		self.movieNames= {} 
		with  open("u.item") as f:
			for line in f:
				fields=line.split('|')
				self.movieNames[fields[0]] = fields[1].decode('utf-8', 'ignore')


	def reducer_count_ratings(self,key,values):
		yield None,(sum(values),self.movieNames[key])

	
	def  reducer_find_max(self, key, values):
		yield max(values)	


if __name__=='__main__':
	MostPopularMovie.run()

''' PS :Note command to execute the script 
python 8.1_MostPopularMovieNicer.py --items=ml-100k/u.item ml-100k/u.data
'''

