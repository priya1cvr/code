# Data Preprocessing Template

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset

os.chdir("/Users/pbishwal/Documents/Techie/Python/Machine_Learning/ML_A-Z_Udemy/Part_1-Data_Preprocessing/Section2Part_1_Data_Preprocessing/Data_Preprocessing")
dataset = pd.read_csv("data.csv")
# create matrix of features i.e independent variables 
X = dataset.iloc[:,:-1].values
# 1st : is take all rows ,:-1 means take all columns except last ,iloc is location

# craeate dependent variable vector 
Y=dataset.iloc[:,-1].values
'''
-1 is take last col 
>>> Y
array(['No', 'Yes', 'No', 'No', 'Yes', 'Yes', 'No', 'Yes', 'No', 'Yes'], dtype=object)
'''

# handle missing data -replace it by taking mean of the col 
from sklearn.preprocessing import Imputer 
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import StandardScaler

# now we need to create object of Imputer class 
imputer = Imputer(missing_values='NaN',strategy = 'mean',axis=0)
#NaN takes care of missing vaues ,axis=0 i.e mean of col , 1 => mean of rows
# you can take median strategey ,refer help(imputer)

# fit imputer object to X ,but wern't going to fit to whole matrix only where is missing data 
imputer=imputer.fit(X[:,1:3]
# lower bound 1 and uupper bound is 3 i.e it excludes 3rd col ,and takes 2nd col

#Now replace missing data by mean of the col i.e 1st and 2nd col index has missing data 
X[:,1:3]=imputer.transform(X[:,1:3])

'''
 X
array([['France', 44.0, 72000.0],
       ['Spain', 27.0, 48000.0],
       ['Germany', 30.0, 54000.0],
       ['Spain', 38.0, 61000.0],
       ['Germany', 40.0, 63777.77777777778],
       ['France', 35.0, 58000.0],
       ['Spain', 38.77777777777778, 52000.0],
       ['France', 48.0, 79000.0],
       ['Germany', 50.0, 83000.0],
       ['France', 37.0, 67000.0]], dtype=object)
''' 
 


# Country and Purchased (has yes/no) is a categorical variable .so we need to encode it 
# Encode categorical data 

#from sklearn.preprocessing import LabelEncoder 
# create object of LabelEncoder class 

labelencoder_X  = LabelEncoder()
#apply labelencoder on 1st col country i.e index 0
X[:,0]=labelencoder_X.fit_transform(X[:,0])
#array([0, 2, 1, 2, 1, 0, 2, 0, 1, 0]) - encoded values of the countries
'''
As ML is based on mathematical models
problem here is since 2>1>0 it may think germany > Spain > France 
So we need to have dummy encoding which would have .
Make no. of columns to no. of categories i.e 3 cols as 3 countries 
so import one hot encoder class from sklear.preprocessing
France Germany Spain will have 1 0 0 and so on 

''' 
onehotencoder = OneHotEncoder(categorical_features =[0])
# tells to encode index 0 
X=onehotencoder.fit_transform(X).toarray()

'''
X
X 1st row has France so its 1 0 0 
X 2nd row has Spain so its 0 0 1 and so on 
array([[  1 ,   0,   0, 4.40000000e+01,   7.20000000e+04],
       [  0 ,   0 ,  1 ,2.70000000e+01,   4.80000000e+04],
       [  0 ,   1,   0 ,3.00000000e+01,   5.40000000e+04],
...
...

'''

# lets take care of purchased variable i.e dependent variable ,we don't use oneHotEncoder
# since its a dependent variable ML model will know its a category  
labelencoder_y  = LabelEncoder()
Y=labelencoder_y.fit_transform(Y) 

'''
 Y
array([0, 1, 0, 0, 1, 1, 0, 1, 0, 1])
0-No , 1- Yes
'''

# split dataset into training and test set 
# from sklearn.cross_validation import train_test_split 

X_train,X_test,Y_train,Y_test = train_test_split(X,Y,test_size=0.2,random_state=0)
# test_size generally 20-30% ,random_state =0 to make results all same number 

'''
2 observation in test set and 8 obs in train set same fr Y 
>>> X_train
array([[  0.00000000e+00,   1.00000000e+00,   0.00000000e+00,
          4.00000000e+01,   6.37777778e+04],
       [  1.00000000e+00,   0.00000000e+00,   0.00000000e+00,
          3.70000000e+01,   6.70000000e+04],
       [  0.00000000e+00,   0.00000000e+00,   1.00000000e+00,
          2.70000000e+01,   4.80000000e+04],
       [  0.00000000e+00,   0.00000000e+00,   1.00000000e+00,
          3.87777778e+01,   5.20000000e+04],
       [  1.00000000e+00,   0.00000000e+00,   0.00000000e+00,
          4.80000000e+01,   7.90000000e+04],
       [  0.00000000e+00,   0.00000000e+00,   1.00000000e+00,
          3.80000000e+01,   6.10000000e+04],
       [  1.00000000e+00,   0.00000000e+00,   0.00000000e+00,
          4.40000000e+01,   7.20000000e+04],
       [  1.00000000e+00,   0.00000000e+00,   0.00000000e+00,
          3.50000000e+01,   5.80000000e+04]])
>>> X_test
array([[  0.00000000e+00,   1.00000000e+00,   0.00000000e+00,
          3.00000000e+01,   5.40000000e+04],
       [  0.00000000e+00,   1.00000000e+00,   0.00000000e+00,
          5.00000000e+01,   8.30000000e+04]])
>>> Y_train
array([1, 1, 1, 0, 1, 0, 0, 1])
>>> Y_test
array([0, 0])

'''

'''
 Age is going from 27 till 50 and salary from 40K to 90K both of them don't have same scale 
 will cause issue in ML models 
 A lot of ML models are based on euclidean distance 
 Euclidean distance = sqrt((x2-x1)^2 + (y2-y1)^2)

salary sq difference dominates age sq difference so we are going to transform them to have in same range

Standardisation i.e X_stand = 	X-mean(X) / (std deviation(x))
Normalisation i.e X_norm = X-min(X) / (max(X) - min(X))
'''

#Feature Scaling 
# from sklearn.preprocessing import StandardScaler

#create object of above StandardScaler class 
sc_X = StandardScaler()
X_train= sc_X.fit_transform(X_train)

# since training set is already fit  neednt to do it for test set 
X_test = sc_X.transform(X_test)

# Q.Do we need to scale dummy variable - depends on context 

'''
here training and test set has undergone standard scaler so all are in same scale 

>>> X_train
array([[-1.        ,  2.64575131, -0.77459667,  0.26306757,  0.12381479],
       [ 1.        , -0.37796447, -0.77459667, -0.25350148,  0.46175632],
       [-1.        , -0.37796447,  1.29099445, -1.97539832, -1.53093341],
       [-1.        , -0.37796447,  1.29099445,  0.05261351, -1.11141978],
       [ 1.        , -0.37796447, -0.77459667,  1.64058505,  1.7202972 ],
       [-1.        , -0.37796447,  1.29099445, -0.0813118 , -0.16751412],
       [ 1.        , -0.37796447, -0.77459667,  0.95182631,  0.98614835],
       [ 1.        , -0.37796447, -0.77459667, -0.59788085, -0.48214934]])
>>> X_test
array([[-1.        ,  2.64575131, -0.77459667, -1.45882927, -0.90166297],
       [-1.        ,  2.64575131, -0.77459667,  1.98496442,  2.13981082]])
'''

# Q . Do we need feature scaling for Y - no as its a dependent variable now 

