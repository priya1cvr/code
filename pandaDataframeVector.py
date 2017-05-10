import pandas as pd

# Examples of vectorized operations on DataFrames:
# Change False to True for each block of code to see what it does

# Adding DataFrames with the column names
if True:
    df1 = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})
    df2 = pd.DataFrame({'a': [10, 20, 30], 'b': [40, 50, 60], 'c': [70, 80, 90]})
    print df1 + df2
''' adds the corresponding cells
	    a   b   c
	0  11  44  77
	1  22  55  88
	2  33  66  99
'''    
# Adding DataFrames with overlapping column names 
if True:
    df1 = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})
    df2 = pd.DataFrame({'d': [10, 20, 30], 'c': [40, 50, 60], 'b': [70, 80, 90]})
    print df1 + df2

'''
	    a   b   c   d
	0 NaN  74  47 NaN
	1 NaN  85  58 NaN
	2 NaN  96  69 NaN
'''
# Adding DataFrames with overlapping row indexes
if True:
    df1 = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]},
                       index=['row1', 'row2', 'row3'])
    df2 = pd.DataFrame({'a': [10, 20, 30], 'b': [40, 50, 60], 'c': [70, 80, 90]},
                       index=['row4', 'row3', 'row2'])
    print df1 + df2

'''
	         a     b     c
	row1   NaN   NaN   NaN
	row2  32.0  65.0  98.0
	row3  23.0  56.0  89.0
	row4   NaN   NaN   NaN
'''	
# --- Quiz ---
# Cumulative entries and exits for one station for a few hours.
entries_and_exits = pd.DataFrame({
    'ENTRIESn': [3144312, 3144335, 3144353, 3144424, 3144594,
                 3144808, 3144895, 3144905, 3144941, 3145094],
    'EXITSn': [1088151, 1088159, 1088177, 1088231, 1088275,
               1088317, 1088328, 1088331, 1088420, 1088753]
})

'''
    Fill in this function to take a DataFrame with cumulative entries
    and exits (entries in the first column, exits in the second) and
    return a DataFrame with hourly entries and exits (entries in the
    first column, exits in the second).
'''

def get_hourly_entries_and_exits(entries_and_exits):
    return entries_and_exits-entries_and_exits.shift(periods=1)
# while doing above subtract it subtract the corresponding  indexes 
# return entries_and_exits.diff()  also works 
	
hourly_entry_and_exit=get_hourly_entries_and_exits(entries_and_exits)
print hourly_entry_and_exit

'''
 
	>>> entries_and_exits
	ENTRIESn   EXITSn
	0   3144312  1088151
	1   3144335  1088159
	2   3144353  1088177
	3   3144424  1088231
	4   3144594  1088275
	5   3144808  1088317
	6   3144895  1088328
	7   3144905  1088331
	8   3144941  1088420
	9   3145094  1088753

	entries_and_exits.shift(periods=1)
    ENTRIESn     EXITSn
0        NaN        NaN
1  3144312.0  1088151.0
2  3144335.0  1088159.0
3  3144353.0  1088177.0
4  3144424.0  1088231.0
5  3144594.0  1088275.0
6  3144808.0  1088317.0
7  3144895.0  1088328.0
8  3144905.0  1088331.0
9  3144941.0  1088420.0


'''	