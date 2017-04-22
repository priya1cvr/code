from mrjob.job import MRJob 
from mrjob.step import MRStep
import re

WORD_REGEXP=re.compile(r"[\w']+")

class MRWordFrequencyCount(MRJob):
	# if you define steps as step it will give ValueError: Step has no mappers and no reducers

	def steps(self):
		return[
			MRStep(mapper=self.mapper_get_words,
				   reducer=self.reducer_count_words),
			MRStep(mapper=self.mapper_make_count_keys,
				   reducer=self.reducer_output_words)
		]
		
	# mapper extracts the key and value we care about ,in this case the key is ignored i.e put as _
	def mapper_get_words(self,_,line):
		#words=line.split()
		words=WORD_REGEXP.findall(line)
		for word in words:
			yield word.lower() ,1

	# reducer is called for each word
	def reducer_count_words(self,word,frequency):	
		yield word,sum(frequency)

	def mapper_make_count_keys(self,word,count):
		yield '%04d'%int(count),word	

	def reducer_output_words(self,count,words):
		for word in words:
			yield count,word

if __name__=='__main__':
	MRWordFrequencyCount.run()			


'''
A “step” consists of a mapper, a combiner, and a reducer. All of those are optional, though you must have at least one. So you could have a step that’s just a mapper, or just a combiner and a reducer.
When you only have one step, all you have to do is write methods called mapper(), combiner(), andreducer().
The mapper() method takes a key and a value as args (in this case, the key is ignored and a single line of text input is the value) and yields as many key-value pairs as it likes. The reduce() method takes a key and an iterator of values and also yields as many key-value pairs as it likes. 
(In this case, it sums the values for each key, which represent the numbers of characters, words, and lines in the input.)
'''