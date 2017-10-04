import numpy as np

# Change False to True for each block of code to see what it does

# Using index arrays
if True:
    a = np.array([1, 2, 3, 4])
    b = np.array([True, True, True, True])
    
    print a[b]
	# o/p -[1,2,3,4] since all values of b are True
    print a[np.array([True, True, True, True])]
	# o/p same as above 
    
# Creating the index array using vectorized operations
if True:
    a = np.array([1, 2, 3, 2, 1])
    b = (a >= 2)
	# vector a compared with scalar >=2 gives another vector b with boolean values 
    # i.e [False,True,True,True,False]
    print a[b]
	# prints [2,3,2]
    print a[a >= 2]
	# short hand notation for above and o/p is same
    
# Creating the index array using vectorized operations on another array
if True:
    a = np.array([1, 2, 3, 4, 5])
    b = np.array([1, 2, 3, 2, 1])
    
    print b == 2
	#compares if the vector b equals 2 and returns a boolean vector with True where value mathces
	#[False  True False  True False]
    print a[b == 2]
	#[2,4]



# Time spent in the classroom in the first week for 20 students
time_spent = np.array([
       12.89697233,    0.        ,   64.55043217,    0.        ,
       24.2315615 ,   39.991625  ,    0.        ,    0.        ,
      147.20683783,    0.        ,    0.        ,    0.        ,
       45.18261617,  157.60454283,  133.2434615 ,   52.85000767,
        0.        ,   54.9204785 ,   26.78142417,    0.
])

# Days to cancel for 20 students
days_to_cancel = np.array([
      4,   5,  37,   3,  12,   4,  35,  38,   5,  37,   3,   3,  68,
     38,  98,   2, 249,   2, 127,  35
])

'''
    Fill in this function to calculate the mean time spent in the classroom
    for students who stayed enrolled at least (greater than or equal to) 7 days.
    Unlike in Lesson 1, you can assume that days_to_cancel will contain only
    integers (there are no students who have not canceled yet).
    
    The arguments are NumPy arrays. time_spent contains the amount of time spent
    in the classroom for each student, and days_to_cancel contains the number
    of days until each student cancel. The data is given in the same order
    in both arrays.
'''

def mean_time_for_paid_students(time_spent, days_to_cancel):
	time_spent_7=time_spent[days_to_cancel>=7]
	print "time spend for greater >7 days:" ,time_spent_7.mean()
    

mean_time_for_paid_students(time_spent,days_to_cancel)