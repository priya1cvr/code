import numpy as np
import pandas as pd

df = pd.DataFrame({
    'a': [4, 5, 3, 1, 2],
    'b': [20, 10, 40, 50, 30],
    'c': [25, 20, 5, 15, 10]
})

# Change False to True for this block of code to see what it does

# DataFrame apply() - use case 2
if True:   
    print df.apply(np.mean) # prints mean for each col 
    print df.apply(np.max)  # prints max for each row 

'''
    Fill in this function to return the second-largest value of each 
    column of the input DataFrame.
'''

    
def second_largest(df):
	second=df.sort_values(ascending=False).iloc[1]
	return second
	
second_largest_item= df.apply(second_largest)
print second_largest_item

'''
a     4
b    40
c    20
dtype: int64
in python shell df.sort_values(ascending=False).iloc[1] doesn't work 
but df.sort_values(by=['a','b','c'],ascending=False).iloc[1] -works 
'''