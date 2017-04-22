''' Making BFS a MR problem 
1.Represent each line of the input graph as a BFS Node,with a color and distance .
e.g 
5988 748 1722 3752 4655 5743 1872 3413 5527 6368 6085 4319 4728 1636 2397 3364 4001 1614 1819 1585 732 
becomes 
5988 |748 1722 3752 4655 5743 1872 3413 5527 6368 6085 4319 4728 1636 2397 3364 4001 1614 1819 1585 732| 9999 | WHITE

Initial Conditions:
1.All nodes initially have a distance 9999(infinite) and color white ,except the node we're starting from -the character we're measuring 
  degrees of seperation from .The starting character has color GRAY and distance 0 .

For each Degree of Seperation we Iterate 
1. The Mapper finds all GRAY Nodes ,update their distance ,and mark their connections GRAY .Then the original GRAY Node is marked BLACK. 
2. The Reducer ensures nodes reached by multiple nodes retain the darkest color ,and shortest distance .
3. Write the output to a file ,and then use that as input for the next degree. 

How do we know when we are done ? 
A counter is used to indicate how many times we hit the character we're looking for .
once it has the result in the output ,we know we found our superhero,and the degrees of seperation(distance) from the one we started from .

Counters can be incremented across the entire map/reduce job ,no matter how many computers are involved in it . 
'''  

from mrjob.job import MRJob
from mrjob.protocol import RawValueProtocol

class Node():
	def __init__(self):
		self.characterID=''
		self.connections=[]
		self.distance=9999
		self.color='WHITE'
	
	#Format is ID|EDGES|DISTANCE|COLOR
	def fromLine(self,line):
		fields=line.split('|')
		if(len(fields)==4):
			self.characterID=fields[0]
			#keeping connections as list 
			self.connections=fields[1].split(',')
			self.distance=int(fields[2])
			self.color=fields[3]

	def  getLine(self):
		connections=','.join(self.connections)
		return '|'.join((self.characterID,connections,str(self.distance),self.color))	

class MRBFSIteration(MRJob):
	INPUT_PROTOCOL = RawValueProtocol
	OUTPUT_PROTOCOL = RawValueProtocol

	def configure_options(self):
		super(MRBFSIteration,self).configure_options()
		self.add_passthrough_option('--target',help="ID of character we are searching for")	
		
	def mapper(self,_,line):
		node=Node()
		node.fromLine(line)
		#If this node needs to be expanded...
		if(node.color=='GRAY'):
			for connection in node.connections:
				vnode=Node()
				vnode.characterID=connection
				vnode.distance=int(node.distance)+1
				vnode.color='GRAY'

				if(self.options.target==connection):
					counterName=("Target ID" + connection+"was hit with a distance "+ str(vnode.distance))
					self.increment_counter('Degree of Seperation',counterName,1)
				yield connection,vnode.getLine()
				
			#We've processed this node, so color it black
			node.color = 'BLACK'
		
		#Emit the input node so we don't lose it.
		yield node.characterID, node.getLine()
	
	def reducer(self,key,values):
		edges=[]
		distance=9999
		color='WHITE'

		for value in values:
			node=Node()
			node.fromLine(value)

			if(len(node.connections)>0):
				#edges =node.connections
				edges.extend(node.connections)

			if(node.distance < distance):
				distance=node.distance

			if(node.color=='BLACK'):
				color='BLACK'

			if(node.color=='GRAY' and color=='WHITE'):
				color='GRAY'

		node=Node()
		node.characterID=key
		node.distance=distance
		node.color=color

		#node.connections = edges[:500] (there is bug in mrjob for Windows where sorting fails with too much data so limited to 500)

		yield key, node.getLine()


if __name__ == '__main__':
    MRBFSIteration.run()		




'''
command to call 

'''











