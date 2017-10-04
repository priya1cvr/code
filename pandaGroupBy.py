import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

values = np.array([1, 3, 2, 4, 1, 6, 4])
example_df = pd.DataFrame({
    'value': values,
    'even': values % 2 == 0,
    'above_three': values > 3 
}, index=['a', 'b', 'c', 'd', 'e', 'f', 'g'])


# Change False to True for each block of code to see what it does

# Examine DataFrame
if True:
    print example_df
'''  print example_df
		above_three   even  value
	a       False  False      1
	b       False  False      3
	c       False   True      2
	d        True   True      4
	e       False  False      1
	f        True   True      6
	g        True   True      4
'''    
# Examine groups
if True:
    grouped_data = example_df.groupby('even')
    # The groups attribute is a dictionary mapping keys to lists of row indexes
    print grouped_data.groups
# {False: ['a', 'b', 'e'], True: ['c', 'd', 'f', 'g']} 
    
# Group by multiple columns
if True:
    grouped_data = example_df.groupby(['even', 'above_three'])
    print grouped_data.groups
# groups even,above_three in a group 
#{(True, False): ['c'], (False, False): ['a', 'b', 'e'], (True, True): ['d', 'f', 'g']}    

# Get sum of each group
if True:
    grouped_data = example_df.groupby('even')
    print grouped_data.sum()
'''
				above_three  value
	even
	False          0.0      5
	True           3.0     16
	0.0- none of above_three numbers are even hence 0
	3.- as 3 value are above_three and even 
'''    
# Limit columns in result
if True:
    grouped_data = example_df.groupby('even')
    
    # You can take one or more columns from the result DataFrame
    print grouped_data.sum()['value']
    print '\n' # Blank line to separate results
    print grouped_data['value'].sum()

'''
	even
	False     5
	True     16
	Name: value, dtype: int32
'''
    
    
    # You can also take a subset of columns from the grouped data before 
    # collapsing to a DataFrame. In this case, the result is the same.
    
    #same output as above 
	
filename = 'nyc_subway_weather.csv'
subway_df = pd.read_csv(filename)

### Write code here to group the subway data by a variable of your choice, then
### either print out the mean ridership within each group or create a plot.
y=subway_df.groupby('fog').mean()['ENTRIESn_hourly'] 
''' print y ,so graph will show the below 
	fog
	0    1889.116150
	1    1631.980907
'''
#- this will contain only mean values for fog for ENTRIESn_hourly col 
y.plot()
plt.show()