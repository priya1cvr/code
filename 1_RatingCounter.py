''' First Map Reduce program '''
# This code shows how many 1 * ,2* rating of movies ...

from mrjob.job import MRJob 

class MRRatingCounter(MRJob):
	# mapper extracts the key and value we care about ,here key is rating and value is its occurence 
	def mapper(self,key,line):
		(userID,movieID,rating,timestamp)=line.split('\t')
		yield rating,1

	def reducer(self,rating,occurences):
		yield rating,sum(occurences)

if __name__=='__main__':
	MRRatingCounter.run()			


''' input to mapper is below: (3rd field is rating )
196	242	3	881250949
186	302	3	891717742
22	377	1	878887116
244	51	2	880606923
mapper then does a yield -> (rating 1) i.e yield is a generator function) .
output of mapper is 3:1, 3:1 ,	1:1,2:1 
2.next step is  sort and group data i.e 
	1:1, 2:1,3:1,1 -- these things mapper does autmoatically (MRJob module )
3.	reducer does rating,sum(occurences) i.e 
	1:1,2:1,3:2 
'''	