from mrjob.job import MRJob 

class MRFriendsByAge(MRJob):
	# mapper extracts the key and value we care about ,here key is rating and value is its occurence ,in this case the key is ignored i.e put as _
	def mapper(self,_,line):
		(ID,name,age,numFriends)=line.split(',')
		yield age,float(numFriends)

	def reducer(self,age,numFriends):
		total=0
		numElements=0
		# numFriends is actually the list of number of friends of that age 
		for x in numFriends:
			total +=x 
			numElements +=1

		yield age,total/numElements	

if __name__=='__main__':
	MRFriendsByAge.run()			
