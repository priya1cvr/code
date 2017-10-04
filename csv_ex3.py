# This program counts the unique account key in daily_engagement using pandas
import pandas as pd 
import unicodecsv

def read_csv(filename):
    with open(filename, 'rb') as f:
        reader = unicodecsv.DictReader(f)
        return list(reader)
		
daily_engagement=pd.read_csv('daily_engagement_full.csv')
print len(daily_engagement['acct'].unique())

'''
1-D data structures for pandas and numpy comparison 
pandas						Numpy
series						array 
series are built on top of numpy arrays.
Numpy array are similar to python list 
			Numpy array  vs python list :
Similiraties 							Difference 
Access elements by position			-numpy array each element should have same type .
e.g a[0]->'AL'						 e.g if there is an array then all the elements should be either
Access a range of elements 			  string  ,int ,boolean etc but in list it is a mixture of all
a[1:3] ->'Ak','AZ'					-includes convenient function e.g mean() std()
use loops							-numpy array can be multi dimensional 
for x in a 


x=max(employment)
    itemindex = np.where(employment==x)
    max_country = countries[itemindex]      # Replace this with your code
    max_value = x   # Replace 
'''