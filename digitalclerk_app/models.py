from django.db import models

class OfficeHours(models.Model):
	custom_profile_fk = models.IntegerField()
	module_code = models.CharField(max_length=50)
	start_time = models.CharField(max_length=50)
	end_time = models.CharField(max_length=50)
	start_date = models.DateField()
	location = models.CharField(max_length=100)
	title = models.CharField(max_length=50)
