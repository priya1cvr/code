import numpy as np

# First 20 countries with employment data
countries = np.array([
    'Afghanistan', 'Albania', 'Algeria', 'Angola', 'Argentina',
    'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas',
    'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium',
    'Belize', 'Benin', 'Bhutan', 'Bolivia',
    'Bosnia and Herzegovina'
])

# Employment data in 2007 for those 20 countries
employment = np.array([
    55.70000076,  51.40000153,  50.5       ,  75.69999695,
    58.40000153,  40.09999847,  61.5       ,  57.09999847,
    60.90000153,  66.59999847,  60.40000153,  68.09999847,
    66.90000153,  53.40000153,  48.59999847,  56.79999924,
    71.59999847,  58.40000153,  70.40000153,  41.20000076
])

# Change False to True for each block of code to see what it does

# Accessing elements

print countries[0]
print countries[3]

# Slicing

print countries[0:3]
print countries[:3]
print countries[17:]
print countries[:]

# Element types

print countries.dtype
#gives S22 ,S means String and 22 is the length of longest character
print employment.dtype
#gives float64, 64 is the length of longest character
print np.array([0, 1, 2, 3]).dtype
print np.array([1.0, 1.5, 2.0, 2.5]).dtype
print np.array([True, False, True]).dtype
#gives bool 
print np.array(['AL', 'AK', 'AZ', 'AR', 'CA']).dtype
#gives S2

# Looping

for country in countries:
    print 'Examining country {}'.format(country)

for i in range(len(countries)):
    country = countries[i]
    country_employment = employment[i]
    print 'Country {} has employment {}'.format(country,
            country_employment)

# Numpy functions

print employment.mean()
print employment.std()
print employment.max()
print employment.sum()

def max_employment(countries, employment):
	#argmax gives the position of max value
	#i=employment.argmax()
	#return (countries[i], employment[i])
	# the below code as gives result
	x=max(employment)
	itemindex = np.where(employment==x)
	max_country = countries[itemindex]       
	max_value = x   
	return (max_country,max_value)
	
p=list(max_employment(countries,employment))
print "The country " ,p[0] ,"has max employment ",p[1] 
  
