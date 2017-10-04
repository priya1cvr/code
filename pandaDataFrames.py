import pandas as pd

# Subway ridership for 5 stations on 10 different days
ridership_df = pd.DataFrame(
    data=[[   0,    0,    2,    5,    0],
          [1478, 3877, 3674, 2328, 2539],
          [1613, 4088, 3991, 6461, 2691],
          [1560, 3392, 3826, 4787, 2613],
          [1608, 4802, 3932, 4477, 2705],
          [1576, 3933, 3909, 4979, 2685],
          [  95,  229,  255,  496,  201],
          [   2,    0,    1,   27,    0],
          [1438, 3785, 3589, 4174, 2215],
          [1342, 4043, 4009, 4665, 3033]],
    index=['05-01-11', '05-02-11', '05-03-11', '05-04-11', '05-05-11',
           '05-06-11', '05-07-11', '05-08-11', '05-09-11', '05-10-11'],
    columns=['R003', 'R004', 'R005', 'R006', 'R007']
)

# Change False to True for each block of code to see what it does

# DataFrame creation
if True:
    # You can create a DataFrame out of a dictionary mapping column names to values
    df_1 = pd.DataFrame({'A': [0, 1, 2], 'B': [3, 4, 5]})
    print df_1
	# You can also use a list of lists or a 2D NumPy array
    df_2 = pd.DataFrame([[0, 1, 2], [3, 4, 5]], columns=['A', 'B', 'C'])
    print df_2

''' 
	df_1 output 
	A & B are 2 columns
	   A  B
	0  0  3
	1  1  4
	2  2  5
	
	df_2 output
	A,B,C are 3 columns
	   A  B  C
	0  0  1  2
	1  3  4  5
'''
    
   

# Accessing elements
if True:
    print ridership_df.iloc[0]
	#prints all the elements of 0th row 
    print ridership_df.loc['05-05-11']
	#print entire row corresponding to index '05-05-11',access elements by location
    print ridership_df['R003']
	#prints entire col corresponding to R003
    print ridership_df.iloc[1, 3]
	#2328 prints data corresponding to 1st row 3rd col 
    
# Accessing multiple rows
if True:
    print ridership_df.iloc[1:4]
    #prints all rows and col starting from 1st row till n-1th row i.e 1st row till 3rd
'''
			   R003  R004  R005  R006  R007
	05-02-11  1478  3877  3674  2328  2539
	05-03-11  1613  4088  3991  6461  2691
	05-04-11  1560  3392  3826  4787  2613
'''	
# Accessing multiple columns
if True:
    print ridership_df[['R003', 'R005']]
    # prints cols of R003 and R005
	
# Pandas axis
if True:
    df = pd.DataFrame({'A': [0, 1, 2], 'B': [3, 4, 5]})
    print df.sum() # sums data corresponding to 2 cols A :3 ,B:12
    print df.sum(axis=1) # sums data for each row 
    print df.values.sum() # sums up all the rows and columns 
'''
	print df
	   A  B
	0  0  3
	1  1  4
	2  2  5
	
	df.sum(axis=1)
	0    3
	1    5
	2    7
''' 

'''
    Fill in this function to find the station with the maximum riders on the
    first day, then return the mean riders per day for that station. Also
    return the mean ridership overall for comparsion.
    
    This is the same as a previous exercise, but this time the
    input is a Pandas DataFrame rather than a 2D NumPy array.
'''   
def mean_riders_for_max_station(ridership_df):
	#first get which station has max riders on 1st day i.e 0th row 
	maxfirstday=ridership_df.iloc[0].argmax() # gives R006 col 
	overall_mean = ridership_df.values.mean() # values gives overall mean , only .mean gives for each col 
	mean_for_max = ridership_df[maxfirstday].mean()
	#it gives a mean for all the max rides 
	return (overall_mean, mean_for_max)

finalResult=mean_riders_for_max_station(ridership_df)
print "The overall mean and mean rider for max is ",finalResult