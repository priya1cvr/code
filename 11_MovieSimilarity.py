from mrjob.job import MRJob 
from mrjob.step import MRStep
from math import sqrt 

from itertools import combinations 

class MovieSimilarities(MRJob):
	"""docstring for MovieSimilarities"""

	def configure_options(self):
		super(MovieSimilarities,self).configure_options()
		self.add_file_option('--items',help="Path to u.item")	
	
	def load_movie_names(self):
		#Load Database of Movie Names 
		self.movieNames = {}
		with  open("u.item") as f:
			for line in f:
				fields=line.split('|')
				self.movieNames[fields[0]] = fields[1].decode('utf-8', 'ignore')

	def steps(self):
		return [
            MRStep(mapper=self.mapper_parse_input,
                   reducer=self.reducer_ratings_by_user),
            MRStep(mapper=self.create_item_pairs,
                   reducer=self.reducer_compute_similarity),
            MRStep(mapper=self.mapper_sort_similarities,
            	   mapper_init=self.load_movie_names,
                   reducer=self.reducer_output_similarities)
           ]
	
	#i/p to mapper is u.data	
	def mapper_parse_input(self,key,line):
		# Outputs userID => (movieID,rating)
		(userID,movieID,rating,timestamp)=line.split('\t')	
		yield userID,(movieID,float(rating))

	#above mapper o/p is input to this reducer 
	def reducer_ratings_by_user(self,user_id,itemRatings):
		# Group (item,rating) pairs by userID
		ratings=[]

		for movieID,rating in itemRatings:
			ratings.append((movieID,rating))

		yield user_id,ratings

	def create_item_pairs(self,user_id,itemRatings):
		# Find every pair of movies each user has seen,and emit 
		# each pair with its associated ratings 

		# combinations finds every possible pair from the list of movies this user viewed e.g combination((12,13,14),2)	=(12,13) (12,14) (13,14)	
		for itemRating1,itemRating2 in combinations(itemRatings,2):
			movieID1=itemRating1[0]
			rating1=itemRating1[1]
			movieID2=itemRating2[0]
			rating2=itemRating2[1]

			#produce both orders so sims are bi-directional 
			yield (movieID1,movieID2) ,(rating1,rating2)
			yield (movieID2,movieID1) ,(rating2,rating1)


	def cosine_similarity(self, ratingPairs):
		# Computes the cosine similarity metric between two rating vectors.
		numPairs = 0

		sum_xx = sum_yy = sum_xy = 0
		for ratingX, ratingY in ratingPairs:
			sum_xx += ratingX * ratingX
			sum_yy += ratingY * ratingY
			sum_xy += ratingX * ratingY
			numPairs += 1

		numerator = sum_xy
		denominator = sqrt(sum_xx) * sqrt(sum_yy)

		score = 0
		if (denominator):
			score = (numerator / (float(denominator)))

		return (score, numPairs)

	def reducer_compute_similarity(self,moviePair,ratingPairs):
    	#compute similarity score between rating vectors for each movie pair viewed by multiple people o/p movie pair score,no.of co-ratings 
		score,numPairs=self.cosine_similarity(ratingPairs) 

    	# Enforce a minimum score and minimum no. of co-ratings to ensure quality 
		if(numPairs>10 and score>0.95):
			yield moviePair,(score,numPairs)

	def mapper_sort_similarities(self,moviePair,scores):
    	# shuffle things around so the key is (movie1,score ) so we have meaningfully sorted results 
		scores,n=scores 
		movie1,movie2=moviePair

		yield (self.movieNames[int(movie1)],score) ,(self.movieNames[int(movie2)],n)

	def reducer_output_similarities(self,movieScore,similarN):
    	#output the results. Movie=>similar Movie,score,no.of co-ratings 
		movie1,score=movieScore

		for movie2,n in similarN:
			yield movie1,(movie2,score,n)	


if __name__ == '__main__':
    MovieSimilarities.run()		

'''
command to call 
python 11_MovieSimilarity.py --items=ml-100k/u.item ml-100k/u.data

'''




			