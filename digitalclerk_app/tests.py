from django.test import TestCase
from .models import UserProfile, OfficeHours, Request, Interaction
from .utils import *

# *********************************************************
# **************** DJANGO MODEL TEST CASES ****************
# *********************************************************

class UserProfileTest(TestCase):
	def setUp(self):
		UserProfile.objects.create(upi="student1",
		 username="teststudent",
		 email="student1@gmail.com",
		 department="test department",
		 full_name="testname1",
		 status="Student"
		)
		UserProfile.objects.create(upi="staff1",
		 username="teststaff",
		 email="staff1@gmail.com",
		 department="test department",
		 full_name="testname2",
		 status="Staff"
		)

	def test_user_profile_str_representation(self):
		student = UserProfile.objects.get(upi="student1")
		staff = UserProfile.objects.get(upi="staff1")
		self.assertEqual(str(student), "User's fullname is testname1, user's status is Student and user's email is student1@gmail.com")
		self.assertEqual(str(staff), "User's fullname is testname2, user's status is Staff and user's email is staff1@gmail.com")

class OfficeHourTest(TestCase):
	def setUp(self):
		OfficeHours.objects.create(custom_profile_fk=1,
		  module_code="COMP101P",
		  title="test title",
		  location="test location",
		  start_time = "9:00:00",
		  end_time = "9:30:00",
		  start_date = "2018-02-10"
		)

	def test_office_hour_str_representation(self):
		test_office_hour = OfficeHours.objects.get(custom_profile_fk=1)
		self.assertEqual(str(test_office_hour), "Module code:COMP101P title:test title location:test location")

	def test_office_hour_date_type(self):
		test_office_hour = OfficeHours.objects.get(custom_profile_fk=1)
		office_hour_date_type = str(type(test_office_hour.start_date))
		self.assertEqual(office_hour_date_type, "<class 'datetime.date'>")

class HelpRequestTest(TestCase):
	def setUp(self):
		OfficeHours.objects.create(id=100,
		  custom_profile_fk=1,
		  module_code="COMP101P",
		  title="test title",
		  location="test location",
		  start_time = "9:00:00",
		  end_time = "9:30:00",
		  start_date = "2018-02-10"
		)

		Request.objects.create(office_hour_id=100,
		  request_user=1,
		  lecturer=1,
		  request_title="test title",
		  time_raised = "2017-11-18 22:40:03",
		  request_description = "test description",
		  status = 0,
		  tried_solutions = "test solutions"
		)

	def test_request_str_representation(self):
		test_request = Request.objects.get(office_hour_id=100)
		self.assertEqual(str(test_request), "Title: test title description:test description tried solutions:test solutions")

	def test_request_datetime_type(self):
		test_request = Request.objects.get(office_hour_id=100)
		test_request_time_type = str(type(test_request.time_raised))
		self.assertEqual(test_request_time_type, "<class 'datetime.datetime'>")

	def test_request_status_code_closed(self):
		test_request = Request.objects.get(office_hour_id=100)
		status = test_request.getStatus(test_request.status)
		self.assertEqual(status, "Closed")

	def test_request_status_code_open(self):
		test_request = Request.objects.get(office_hour_id=100)
		test_request.status = 1
		status = test_request.getStatus(test_request.status)
		self.assertEqual(status, "Open")

	def test_request_status_code_pending(self):
		test_request = Request.objects.get(office_hour_id=100)
		test_request.status = 2
		status = test_request.getStatus(test_request.status)
		self.assertEqual(status, "Pending")

class Interactiontest(TestCase):
	def setUp(self):
		OfficeHours.objects.create(id=100,
		  custom_profile_fk=1,
		  module_code="COMP101P",
		  title="test title",
		  location="test location",
		  start_time = "9:00:00",
		  end_time = "9:30:00",
		  start_date = "2018-02-10"
		)

		Request.objects.create(id=100,
		  office_hour_id=100,
		  request_user=1,
		  lecturer=1,
		  request_title="test title",
		  time_raised = "2017-11-18 22:40:03",
		  request_description = "test description",
		  status = 0,
		  tried_solutions = "test solutions"
		)

		Interaction.objects.create(id=100,
		  office_hour_id=100,
		  request_id=100,
		  lecturer=1,
		  time_opened = "2017-11-18 22:40:03",
		  status = 0
		)

	def test_interaction_time_type(self):
		test_interaction = Interaction.objects.get(pk=100)
		test_interaction_time_type = str(type(test_interaction.time_opened))
		self.assertEqual(test_interaction_time_type, "<class 'datetime.datetime'>")

	def test_interaction_status_code_closed(self):
		test_interaction = Interaction.objects.get(office_hour_id=100)
		status = test_interaction.getStatus(test_interaction.status)
		self.assertEqual(status, "Pending")

	def test_intercation_status_code_open(self):
		test_interaction = Interaction.objects.get(office_hour_id=100)
		test_interaction.status = 1
		status = test_interaction.getStatus(test_interaction.status)
		self.assertEqual(status, "Resolved")

	def test_interaction_status_code_pending(self):
		test_interaction = Interaction.objects.get(office_hour_id=100)
		test_interaction.status = 2
		status = test_interaction.getStatus(test_interaction.status)
		self.assertEqual(status, "Abandon")


# ************************************************************
# **************** Unit Functional Test Cases ****************
# ************************************************************

class TimeDifferenceTest(TestCase):
	def test_difference_less_than_one_minute(self):
		start_time = "2017-11-18 22:42:15"
		end_time = "2017-11-18 22:42:55"
		start_time_stamp = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
		end_time_stamp = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
		result = get_time_difference_seconds(start_time_stamp,end_time_stamp)
		self.assertEqual(result,40)

	def test_difference_less_more_than_minute(self):
		start_time = "2017-11-18 22:42:15"
		end_time = "2017-11-18 22:43:20"
		start_time_stamp = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
		end_time_stamp = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
		result = get_time_difference_seconds(start_time_stamp,end_time_stamp)
		self.assertEqual(result,65)

	def test_difference_less_in_hours(self):
		start_time = "2017-11-18 22:42:15"
		end_time = "2017-11-18 23:42:16"
		start_time_stamp = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
		end_time_stamp = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
		result = get_time_difference_seconds(start_time_stamp,end_time_stamp)
		self.assertEqual(result,3601)

class OfficeHourIsOverTest(TestCase):
	def setUp(self):
		OfficeHours.objects.create(id=1,
		  custom_profile_fk=1,
		  module_code="COMP101P",
		  title="test title",
		  location="test location",
		  start_time = "9:00",
		  end_time = "9:30",
		  start_date = "2017-02-10"
		)

		OfficeHours.objects.create(id=2,
		  custom_profile_fk=2,
		  module_code="COMP101P",
		  title="test title",
		  location="test location",
		  start_time = "9:00",
		  end_time = "9:30",
		  start_date = "2020-02-10"
		)

	def test_office_hour_is_over(self):
		test_office_hour = OfficeHours.objects.get(id=1)
		result = check_office_hour_is_over(test_office_hour)
		self.assertEqual(result, 1)

	def test_office_hour_is_not_over(self):
		test_office_hour = OfficeHours.objects.get(id=2)
		result = check_office_hour_is_over(test_office_hour)
		self.assertEqual(result, 0)
