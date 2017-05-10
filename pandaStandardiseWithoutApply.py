import pandas as pd

# Adding using +
if True:
    s = pd.Series([1, 2, 3, 4])
    df = pd.DataFrame({
        0: [10, 20, 30, 40],
        1: [50, 60, 70, 80],
        2: [90, 100, 110, 120],
        3: [130, 140, 150, 160]
    })
    
    print df
    print '' # Create a blank line between outputs
    print df + s

''' adds  each col of series to col of DataFrame
	    0   1    2    3
	0  11  52   93  134
	1  21  62  103  144
	2  31  72  113  154
	3  41  82  123  164
'''    
# Adding with axis='index'
if True:
    s = pd.Series([1, 2, 3, 4])
    df = pd.DataFrame({
        0: [10, 20, 30, 40],
        1: [50, 60, 70, 80],
        2: [90, 100, 110, 120],
        3: [130, 140, 150, 160]
    })
    
    print df
    print '' # Create a blank line between outputs
    print df.add(s, axis='index')
    # The functions sub(), mul(), and div() work similarly to add()
'''
	adds  each row of series to row of DataFrame 
		0   1    2    3
	0  11  51   91  131
	1  22  62  102  142
	2  33  73  113  153
	3  44  84  124  164
'''    
# Adding with axis='columns'
if True:
    s = pd.Series([1, 2, 3, 4])
    df = pd.DataFrame({
        0: [10, 20, 30, 40],
        1: [50, 60, 70, 80],
        2: [90, 100, 110, 120],
        3: [130, 140, 150, 160]
    })
    
    print df
    print '' # Create a blank line between outputs
    print df.add(s, axis='columns')
    # The functions sub(), mul(), and div() work similarly to add()
''' adds  each col of series to col of DataFrame
	    0   1    2    3
	0  11  52   93  134
	1  21  62  103  144
	2  31  72  113  154
	3  41  82  123  164
'''
    
grades_df = pd.DataFrame(
    data={'exam1': [43, 81, 78, 75, 89, 70, 91, 65, 98, 87],
          'exam2': [24, 63, 56, 56, 67, 51, 79, 46, 72, 60]},
    index=['Andre', 'Barry', 'Chris', 'Dan', 'Emilio', 
           'Fred', 'Greta', 'Humbert', 'Ivan', 'James']
)

'''
    Fill in this function to standardize each column of the given
    DataFrame. To standardize a variable, convert each value to the
    number of standard deviations it is above or below the mean.
    
    This time, try to use vectorized operations instead of apply().
    You should get the same results as you did before.
'''
def standardize(dfx):
    return (dfx-dfx.mean())/dfx.std()

'''
    Optional: Fill in this function to standardize each row of the given
    DataFrame. Again, try not to use apply().
    
    This one is more challenging than standardizing each column!
'''
def standardize_rows(df):   
	mean_diff= df.sub(df.mean(axis='columns'),axis='index')
	p=mean_diff.div(df.std(axis='columns'),axis='index')
	return p

print "standardize rows" ,"\n", standardize_rows(grades_df)
print " "
print "standardize column" ,"\n",standardize(grades_df)

'''
standardize rows
            exam1     exam2
Andre    0.707107 -0.707107
Barry    0.707107 -0.707107
Chris    0.707107 -0.707107
Dan      0.707107 -0.707107
Emilio   0.707107 -0.707107
Fred     0.707107 -0.707107
Greta    0.707107 -0.707107
Humbert  0.707107 -0.707107
Ivan     0.707107 -0.707107
James    0.707107 -0.707107

standardize column
            exam1     exam2
Andre   -2.196525 -2.186335
Barry    0.208891  0.366571
Chris    0.018990 -0.091643
Dan     -0.170911 -0.091643
Emilio   0.715295  0.628408
Fred    -0.487413 -0.418938
Greta    0.841896  1.413917
Humbert -0.803916 -0.746234
Ivan     1.284999  0.955703
James    0.588694  0.170194
'''