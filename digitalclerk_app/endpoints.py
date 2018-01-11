import requests
import json
import os

from django.conf import settings
from .models import OfficeHours, Request, Interaction, Feedback, UserProfile, Enrolment

def getPersonalModules(token_code):
	url = settings.UCLAPI_URL + "/timetable/personal"
	params = {
		'token': token_code,
		'client_secret': settings.UCLAPI_CLIENT_SECRET
	}
	modules = requests.get(url, params=params)
	modules_json = modules.json()
	timetable = modules_json['timetable']
	events_array = []
	module_list = []
	for date, events in timetable.items():
		events_array = events_array + events
	for events in events_array:
		module = {
			'module_code': events['module']['module_id'],
			'module_name': events['module']['name']
		}
		module_list.append(module)
	unique_module_list = {v['module_code']:v for v in module_list}.values()
	return unique_module_list

# Stores a user if they are logged in for the first time
def store_user(token_code):
	url = settings.UCLAPI_URL + "/oauth/user/data"
	params = {
		'token': token_code,
		'client_secret': settings.UCLAPI_CLIENT_SECRET
	}
	user_data = requests.get(url, params=params)
	user_data_json = user_data.json()
	user_upi = user_data_json['upi']
	try:
		user_profile = UserProfile.objects.get(upi=user_upi)
	except UserProfile.DoesNotExist:
		print(user_data_json['email'])
		user_profile = UserProfile(
			upi=user_data_json['upi'],
			username=user_data_json['cn'],
			email=user_data_json['email'],
			department=user_data_json['department'],
			full_name=user_data_json['full_name']
		)
		user_profile.save()
		enrolled_modules = getPersonalModules(token_code)
		print('user_id = ' + str(user_profile.id))
		store_modules(enrolled_modules, user_profile)

# Creates enrolment for users who are logged in for the first time, used in above method.
def store_modules(module_list, user_profile):
	for module in module_list:
		module_code = module['module_code']
		module_name = module['module_name']
		enrolment = Enrolment(
			user_id=user_profile.id,
			module_code=module_code,
			module_name=module_name
		)
		enrolment.save()
