from .helper_classes import MockUserProfile, MockModules

from .models import OfficeHours, Request, Interaction

import xlrd
import json
import os

def office_hours_to_dict(office_hours_query_set):
	office_hours_dict_array = []
	user_profile = MockUserProfile()
	for office_hour in office_hours_query_set:
		office_hour_dict = {
			'id': office_hour.id,
			'lecturer_id': office_hour.custom_profile_fk,
			'lecturer': user_profile.getNameFromId(office_hour.custom_profile_fk),
			'title': office_hour.title,
			'date': str(office_hour.start_date),
			'start': (str(office_hour.start_date) + "T" + office_hour.start_time),
			'end': (str(office_hour.start_date) + "T" + office_hour.end_time),
			'location': office_hour.location
		}
		office_hours_dict_array.append(office_hour_dict)
	return office_hours_dict_array

def get_lecturers_for_module(module_code):
	lecturers_dict_array = []
	user_profile = MockUserProfile()
	office_hours_query_set = OfficeHours.objects.filter(module_code=module_code)
	for office_hour in office_hours_query_set:
		lecturer_dict = {
			'id': office_hour.custom_profile_fk,
			'name': user_profile.getNameFromId(office_hour.custom_profile_fk)
		}
		lecturers_dict_array.append(lecturer_dict)
	unique_lecturer_list = {v['id']:v for v in lecturers_dict_array}.values()
	return unique_lecturer_list

def get_prior_requests_count(request_id):
	count = 0
	requests = Request.objects.filter(status__in=[1,2]).order_by('time_raised')
	print(requests)
	if (len(requests) == 0):
		return 0
	for request in requests:
		if (request_id == request.id):
			return count
		else:
			count+=1

def format_requests(requests_query_set):
	formatted_requests = []
	user_profile = MockUserProfile()
	for request in requests_query_set:
		formatted_request = {
			'request': request,
			'owner': user_profile.getNameFromId(request.request_user)
		}
		formatted_requests.append(formatted_request)
	return formatted_requests

def format_interactions(interaction_query_set):
	formatted_interactions = []
	user_profile = MockUserProfile()
	interaction_status_list = ['Pending', 'Resolved', 'Abandoned']
	for interaction in interaction_query_set:
		request = Request.objects.get(pk=interaction.request_id)
		formatted_interaction = {
			'request': request,
			'owner': user_profile.getNameFromId(request.request_user),
			'interaction': interaction,
			'status': interaction_status_list[interaction.status]
		}
		formatted_interactions.append(formatted_interaction)
	return formatted_interactions

def parse_input_file(inputFile):
	workbook = xlrd.open_workbook(file_contents=inputFile.read())
	excelSheet = workbook.sheet_by_index(0)
	headerRow = excelSheet.row(0)
	header1 = headerRow[0].value
	header2 = headerRow[1].value
	header3 = headerRow[2].value
	entries = []
	print(header1 + " | " + header2 + " | " + header3 )
	print("----------------------------------")
	for row in range((excelSheet.nrows - 1)):
		entry = {
			'first_name': excelSheet.cell(row+1,0).value,
			'last_name': excelSheet.cell(row+1,1).value,
			'status': excelSheet.cell(row+1,2).value,
		}
		entries.append(entry)
	print(entries)
	excel_data = {
		'header1': header1,
		'header2': header2,
		'header3': header3,
		'entries': entries,
	}
	return excel_data