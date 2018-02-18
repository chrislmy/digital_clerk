from django.db import models

class OAuthToken(models.Model):
    code = models.CharField(max_length=80)

class HelpStaff(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	status = models.CharField(max_length=50)
	department = models.CharField(max_length=100)
	upi = models.CharField(max_length=20)

class OfficeHours(models.Model):
	custom_profile_fk = models.IntegerField()
	module_code = models.CharField(max_length=50)
	start_time = models.CharField(max_length=50)
	end_time = models.CharField(max_length=50)
	start_date = models.DateField()
	location = models.CharField(max_length=100)
	title = models.CharField(max_length=50)

	def __str__(self):
		return "Module code:" + self.module_code  + " title:" + self.title + " location:" + self.location

class Request(models.Model):
	REQUEST_STATUS = (
		(2, 'Pending'),
	    (1, 'Open'),
	    (0, 'Closed'),
	)
	office_hour = models.ForeignKey(OfficeHours, on_delete=models.CASCADE)
	request_user = models.IntegerField()
	lecturer = models.IntegerField()
	request_title = models.CharField(max_length=150)
	time_raised = models.DateTimeField()
	request_description = models.CharField(max_length=300)
	status = models.IntegerField(choices=REQUEST_STATUS, default=1)
	tried_solutions = models.CharField(max_length=300)

	def __str__(self):
		return "Title: " + self.request_title + " description:" + self.request_description + " tried solutions:" + self.tried_solutions

	def getStatus(self, status_code):
		statuses = ['Closed', 'Open', 'Pending']
		return statuses[status_code] 

class Interaction(models.Model):
	INTERACTION_STATUS = (
		(2, 'Abandon'),
	    (1, 'Resolved'),
	    (0, 'Pending'),
	)
	office_hour = models.ForeignKey(OfficeHours, on_delete=models.CASCADE)
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	lecturer = models.IntegerField()
	time_opened = models.DateTimeField()
	time_closed = models.DateTimeField(null=True, blank=True)
	duration_seconds = models.IntegerField(default=0)
	status = models.IntegerField(choices=INTERACTION_STATUS, default=0)

	def getStatus(self, status_code):
		statuses = ['Pending', 'Resolved', 'Abandon']
		return statuses[status_code] 

class Feedback(models.Model):
	request = models.ForeignKey(Request, on_delete=models.CASCADE)
	lecturer = models.IntegerField()
	next_steps = models.CharField(max_length=300, null=True, blank=True)
	foot_note = models.CharField(max_length=300, null=True, blank=True)

class UserProfile(models.Model):
	upi = models.CharField(max_length=15)
	username = models.CharField(max_length=15)
	email = models.CharField(max_length=150)
	department = models.CharField(max_length=150)
	full_name = models.CharField(max_length=150)
	status = models.CharField(max_length=25)

	def __str__(self):
		return "User's fullname is " + self.full_name + ", user's status is " + self.status + " and user's email is " + self.email

class Enrolment(models.Model):
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	module_code = models.CharField(max_length=50)
	module_name = models.CharField(max_length=300)
