from mrjob.job import MRJob 
import re
WORD_REGEXP=re.compile(r"[\w']+")

class WordFrequency(MRJob):

	# mapper extracts the key and value we care about ,in this case the key is ignored i.e put as _
	def mapper(self,_,line):
		#words=line.split()
		words=WORD_REGEXP.findall(line)
		for word in words:
			yield word.lower() ,1

	# reducer is called for each word
	def reducer(self,word,frequency):	
		yield word,sum(frequency)

if __name__=='__main__':
	WordFrequency.run()			
