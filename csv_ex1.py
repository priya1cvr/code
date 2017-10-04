'''
program-1
import unicodecsv
enrollments=[]
#rb means file opened for reading and b flag changes the format how file is read 
#csv documentation page mentions that we need to use the library when using for csv 
f=open('enrollments.csv','rb')
reader=unicodecsv.DictReader(f)
#DictReader which means each row will be a dictionary i.e the values will be represented as 
# key-value pairs 
for row in reader:
	enrollments.append(row)
f.close()
print enrollments[0]

output:
{u'status': u'canceled', u'is_udacity': u'True', u'is_canceled': u'True', u'join_date': u'2014-11-10', u'account_key': u'448', u'cancel_date': u'2015-01-14', u'days_to_cancel': u'65'}

'''

'''
# The above program can be modified as below :
import unicodecsv
#with is more functional style of using to open the file as it closes the file implicitly
with open('enrollments.csv','rb') as f:
	reader=unicodecsv.DictReader(f)
	enrollments=list(reader)
	
#enrollments=list(reader) replaces the for loop 
print enrollments[0]
'''

#Now suppose i want to do the same stuffs for 3 files so instead of copying it 3 times 
# i can write a fucntion to do it 
import unicodecsv
def csv_reader(filename):
	with open(filename,'rb') as f:
		reader=unicodecsv.DictReader(f)
		return list(reader)

# the below are list of dictionary elements 
enrollments=csv_reader('enrollments.csv')	
daily_engagement=csv_reader('daily_engagement.csv')
project_submission=csv_reader('project_submissions.csv')

print enrollments[0]
print daily_engagement[0]
print project_submission[0]	

	
