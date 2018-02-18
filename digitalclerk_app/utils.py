from .helper_classes import MockUserProfile, MockModules

from .models import OfficeHours, Request, Interaction, Feedback, Enrolment, UserProfile, HelpStaff
from django.utils import timezone
from binascii import hexlify
from .endpoints import *

import xlrd, datetime
import json
import os

# State for Oauth2.0 api
def generate_state():
    client_secret = hexlify(os.urandom(32)).decode()
    return client_secret

def office_hours_to_dict(office_hours_query_set):
	office_hours_dict_array = []
	for office_hour in office_hours_query_set:
		office_hour_dict = {
			'id': office_hour.id,
			'lecturer_id': office_hour.custom_profile_fk,
			'lecturer': get_user_full_name(office_hour.custom_profile_fk),
			'title': office_hour.title,
			'date': str(office_hour.start_date),
			'start': (str(office_hour.start_date) + "T" + office_hour.start_time),
			'end': (str(office_hour.start_date) + "T" + office_hour.end_time),
			'location': office_hour.location
		}
		office_hours_dict_array.append(office_hour_dict)
	return office_hours_dict_array

def office_hours_is_over(office_hour_id):
	office_hour = OfficeHours.objects.get(pk=office_hour_id)
	return check_office_hour_is_over(office_hour)

def check_office_hour_is_over(office_hour):
	office_hour_date = str(office_hour.start_date)
	end_time = office_hour.end_time
	end_time_str = office_hour_date + " " + end_time
	end_time_dt = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
	if(datetime.datetime.now() > end_time_dt):
		return 1
	return 0

def get_module_name(module_code):
	module = Enrolment.objects.filter(module_code=module_code)[0] # First element is sufficient
	return module.module_name

def get_lecturers_for_module(module_code):
	lecturers_dict_array = []
	office_hours_query_set = OfficeHours.objects.filter(module_code=module_code)
	for office_hour in office_hours_query_set:
		lecturer_id = office_hour.custom_profile_fk
		lecturer = UserProfile.objects.get(pk=lecturer_id)
		lecturer_dict = {
			'id': lecturer_id,
			'name': lecturer.full_name
		}
		lecturers_dict_array.append(lecturer_dict)
	unique_lecturer_list = {v['id']:v for v in lecturers_dict_array}.values()
	return unique_lecturer_list

def get_module_num_active_office_hours(module_code):
	today_date = datetime.datetime.today().strftime('%Y-%m-%d')
	office_hours = OfficeHours.objects.filter(module_code=module_code, start_date__gt=today_date)
	return len(office_hours)

def get_num_students_in_module(module_code):
	students = Enrolment.objects.filter(module_code=module_code)
	return len(students)

def get_prior_requests_count(office_hour_id, request_id):
	count = 0
	requests = Request.objects.filter(office_hour_id=office_hour_id, status__in=[1,2]).order_by('time_raised')
	if (len(requests) == 0):
		return 0
	for request in requests:
		if (request_id == request.id):
			return count
		else:
			count+=1

def format_requests(requests_query_set):
	formatted_requests = []
	interaction_status_list = ['Pending', 'Resolved', 'Abandoned']
	for request in requests_query_set:
		interaction = None
		feedback = None
		status = ''
		feedback_owner = ''
		try:
			interaction = Interaction.objects.get(request_id=request.id)
			status = interaction_status_list[interaction.status]
		except Interaction.DoesNotExist:
			interaction = None
		try:
			feedback = Feedback.objects.get(request_id=request.id)
			feedback_owner = get_user_full_name(feedback.lecturer)
		except Feedback.DoesNotExist:
			feedback = None
		formatted_request = {
			'request': request,
			'interaction': interaction,
			'feedback': feedback,
			'feedback_owner': feedback_owner, 
			'owner': get_user_full_name(request.request_user),
			'status': status
		}
		formatted_requests.append(formatted_request)
	return formatted_requests

def format_interactions(interaction_query_set):
	formatted_interactions = []
	interaction_status_list = ['Pending', 'Resolved', 'Abandoned']
	for interaction in interaction_query_set:
		request = Request.objects.get(pk=interaction.request_id)
		formatted_interaction = {
			'request': request,
			'owner': get_user_full_name(request.request_user),
			'interaction': interaction,
			'status': interaction_status_list[interaction.status]
		}
		formatted_interactions.append(formatted_interaction)
	return formatted_interactions

def get_time_difference_seconds(start_time, end_time):
	start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
	end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
	start_time_dt = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
	end_time_dt = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
	elapsed_time = divmod((end_time_dt - start_time_dt).total_seconds(),60)
	time_seconds = int(elapsed_time[0])*60 + int(elapsed_time[1])
	return time_seconds

def get_help_staff():
	help_staff_list = HelpStaff.objects.all()
	entries = []
	for help_staff in help_staff_list:
		entry ={
			'first_name': help_staff.first_name,
			'last_name': help_staff.last_name,
			'status': help_staff.status,
			'department': help_staff.department,
			'upi': help_staff.upi,
		}
		entries.append(entry)
	return entries


def parse_input_file(inputFile):
	workbook = xlrd.open_workbook(file_contents=inputFile.read())
	excelSheet = workbook.sheet_by_index(0)
	headerRow = excelSheet.row(0)
	first_name = headerRow[0].value
	last_name = headerRow[1].value
	status = headerRow[2].value
	department = headerRow[3].value
	upi = headerRow[4].value
	entries = []
	print(first_name + " | " + last_name + " | " + status + " | " + upi )
	print("----------------------------------")
	# Clear the table to be updated
	HelpStaff.objects.all().delete()
	for row in range((excelSheet.nrows - 1)):
		help_staff = HelpStaff(first_name=excelSheet.cell(row+1,0).value,
			last_name=excelSheet.cell(row+1,1).value,
			status=excelSheet.cell(row+1,2).value,
			department=excelSheet.cell(row+1,3).value,
			upi=excelSheet.cell(row+1,4).value	
		)
		entry = {
			'first_name': excelSheet.cell(row+1,0).value,
			'last_name': excelSheet.cell(row+1,1).value,
			'status': excelSheet.cell(row+1,2).value,
			'department': excelSheet.cell(row+1,3).value,
			'upi': excelSheet.cell(row+1,4).value,
		}
		entries.append(entry)
		help_staff.save()
	excel_data = {
		'first_name': first_name,
		'last_name': last_name,
		'status': status,
		'department': department,
		'upi': upi,
		'entries': entries
	}
	return excel_data