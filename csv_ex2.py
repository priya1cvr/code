import unicodecsv

def read_csv(filename):
    with open(filename, 'rb') as f:
        reader = unicodecsv.DictReader(f)
        return list(reader)

enrollments = read_csv('enrollments.csv')
daily_engagement = read_csv('daily_engagement.csv')
project_submissions = read_csv('project_submissions.csv')
    
### For each of these three tables, find the number of rows in the table and
### the number of unique students in the table. To find the number of unique
### students, you might want to create a set of the account keys in each table.

uniq_enrolled_students=set()
for enrollment in enrollments:
	uniq_enrolled_students.add(enrollment['account_key'])
	
		
enrollment_num_rows = len(enrollments) 
# for uniq students add account_key to a empty set and add elements of account_key and then count 
enrollment_num_unique_students = len(uniq_enrolled_students)  

# Note : since account_key is stored in daily_engagement as acct instead of account_key as in other 2 tables
# So lets make it uniform and store account_key in all 3 tables i.e change acct to account_key in daily_engagement

for engagement_rec in daily_engagement:
	#copy acct to account_key and then delete acct
	engagement_rec['account_key'] =engagement_rec['acct']
	del(engagement_rec['acct'])
	

uniq_engaged_students=set()
for engagement in daily_engagement:
	uniq_engaged_students.add(engagement['account_key'])
	
engagement_num_rows = len(daily_engagement)             
engagement_num_unique_students =len(uniq_engaged_students) 

uniq_submit_students=set()
for enrollment in project_submissions:
	uniq_submit_students.add(enrollment['account_key'])
	
submission_num_rows = len(project_submissions)             
submission_num_unique_students = len(uniq_submit_students) 

print "enrollment count",enrollment_num_rows , enrollment_num_unique_students 
print "engagement count",engagement_num_rows , engagement_num_unique_students
print "submission count",submission_num_rows , submission_num_unique_students