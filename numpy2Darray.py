import numpy as np

# Subway ridership for 5 stations on 10 different days
ridership = np.array([
    [   0,    0,    2,    5,    0],
    [1478, 3877, 3674, 2328, 2539],
    [1613, 4088, 3991, 6461, 2691],
    [1560, 3392, 3826, 4787, 2613],
    [1608, 4802, 3932, 4477, 2705],
    [1576, 3933, 3909, 4979, 2685],
    [  95,  229,  255,  496,  201],
    [   2,    0,    1,   27,    0],
    [1438, 3785, 3589, 4174, 2215],
    [1342, 4043, 4009, 4665, 3033]
])

# Change False to True for each block of code to see what it does

# Accessing elements
if True:
	print ridership[1, 3]
	#2328
	print ridership[1:3, 3:5]
	#i have doubt on this 
	 #[[2328 2539]
	 #[6461 2691]]
	print ridership[1, :]
    #[1478 3877 3674 2328 2539]
# Vectorized operations on rows or columns
if True:
    print ridership[0, :] + ridership[1, :]
	# [1478 3877 3676 2333 2539]  sums 0th and 1st row 
    print ridership[:, 0] + ridership[:, 1]
	#[   0 5355 5701 4952 6410 5509  324    2 5223 5385] sums 0th and 1st col
    
# Vectorized operations on entire arrays
if True:
    a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    b = np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3]])
    print a + b
''' adds corresponding elements 
[[ 2  3  4]
 [ 6  7  8]
 [10 11 12]]
'''
'''
    Fill in this function to find the station with the maximum riders on the
    first day, then return the mean riders per day for that station. Also
    return the mean ridership overall for comparsion.
    
    Hint: NumPy's argmax() function might be useful:
    http://docs.scipy.org/doc/numpy/reference/generated/numpy.argmax.html
'''
def mean_riders_for_max_station(ridership):
	#1st day is row 0 of the array
	#argmax return the position of max value 
	maxfirstday=ridership[0,:].argmax()
	#now find the mean riders per day for that station
	#so select all rows and maxfirstday i.e col 3
	mean_for_max=ridership[:,maxfirstday].mean()
	overall_mean = ridership.mean() 
	return (overall_mean, mean_for_max)

finalResult=mean_riders_for_max_station(ridership)
print "The overall mean and mean rider for max is ",finalResult