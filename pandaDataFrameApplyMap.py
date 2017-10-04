import pandas as pd

# Change False to True for this block of code to see what it does

# DataFrame applymap()
if True:
    df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [10, 20, 30],
        'c': [5, 10, 15]
    })
    
    def add_one(x):
        return x + 1
        
    print df.applymap(add_one)
    
grades_df = pd.DataFrame(
    data={'exam1': [43, 81, 78, 75, 89, 70, 91, 65, 98, 87],
          'exam2': [24, 63, 56, 56, 67, 51, 79, 46, 72, 60]},
    index=['Andre', 'Barry', 'Chris', 'Dan', 'Emilio', 
           'Fred', 'Greta', 'Humbert', 'Ivan', 'James']
)

'''
    Fill in this function to convert the given DataFrame of numerical
    grades to letter grades. Return a new DataFrame with the converted
    grade.
    
    The conversion rule is:
        90-100 -> A
        80-89  -> B
        70-79  -> C
        60-69  -> D
        0-59   -> F
'''
    
def convert_grades(grades):
	if(grades>=90 and grades<=100):
		grade='A'
	elif(grades>=80 and grades<=89):
		grade='B'
	elif (grades>=70 and grades<=79):
		grade='C'
	elif(grades>=60 and grades<=69):
		grade='D'
	else: grade='F'	
    
	return grade

print grades_df.applymap(convert_grades)

'''

				exam1 exam2
	Andre       F     F
	Barry       B     D
	Chris       C     F
	Dan         C     F
	Emilio      B     D
	Fred        C     F
	Greta       A     C
	Humbert     D     F
	Ivan        A     C
	James       B     D

'''