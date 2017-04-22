'''
First we walk through transforming the Marvel dataset into a format usable for the BFS algorithm.

 Call this with one argument: the character ID you are starting from.
 For example, Spider Man is 5306, The Hulk is 2548. Refer to Marvel-names.txt for others.


'''
import sys 

print 'Creating BFS starting input for character ' +sys.argv[1]

# BFS-iteration-0.txt is the output file produced 
with open("BFS-iteration-0.txt",'w') as out:
	with open("marvel-graph.txt") as f:
		for line in f:
			fields=line.split()
			heroID=fields[0]
			numConnections=len(fields)-1
			connections=fields[-numConnections:]

			color='WHITE'
			distance=9999

			if(heroID==sys.argv[1]):
				color='GRAY'
				distance=0

			if(heroID!=''):
				edges=','.join(connections)
				outStr='|'.join((heroID,edges,str(distance),color))
				out.write(outStr)
				out.write("\n")	
	f.close()
out.close()				


'''
e.g input set :5988 748 1722 3752 4655 5743 1872 3413 5527 6368 6085 4319 4728 1636 2397 3364 4001 1614 1819 1585 732 

print edges will give like :
748,1722,3752,4655,5743,1872,3413,5527,6368,6085,4319,4728,1636,2397,3364,4001,1614,1819,1585,732
print outStr
5988|748,1722,3752,4655,5743,1872,3413,5527,6368,6085,4319,4728,1636,2397,3364,4001,1614,1819,1585,732|9999|WHITE

How to call the script : 
python 10_ProcessMarvel.py 5306 (5306 is the character for Spider Man)
'''
