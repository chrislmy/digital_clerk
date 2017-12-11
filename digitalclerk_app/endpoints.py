import requests
import json
import os

from django.conf import settings

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


