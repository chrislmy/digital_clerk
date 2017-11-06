from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core import serializers

from .forms import AdminUploadFileForm, AddOfficeHourForm
from .helper_classes import MockUserProfile, MockModules
from .models import OfficeHours

import xlrd
import json
import os

def dashboard(request):
	mock_module = MockModules()
	modules_arr = mock_module.listModules
	data = {
		'modules': modules_arr
	}
	return render(request, 'digitalclerk_app/dashboard.html', data)

def module_details(request, module_code):
	user_profile = MockUserProfile()
	user_upi = user_profile.studentProfile()['upi']
	form = AddOfficeHourForm()
	office_hours = OfficeHours.objects.filter(custom_profile_fk=user_upi,module_code=module_code)
	office_hours_dict_array = office_hours_to_dict(office_hours)
	office_hours_json = json.dumps(office_hours_dict_array)
	data = {
		'user_upi': user_upi,
		'module_code': module_code,
		'form': form,
		'office_hours': office_hours_json
	}
	return render(request, 'digitalclerk_app/module_detail.html',data)

def admin_index(request):
	if request.method == 'POST':
		form = AdminUploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			inputFile = request.FILES['file']
			data = parse_input_file(inputFile)
			print(data)
			return render(request, 'digitalclerk_app/uploaded.html', data)
	else:
		form = AdminUploadFileForm()
	return render(request, 'digitalclerk_app/admin-upload.html', {'form': form})
	
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

def add_office_hour(request):
	title = request.POST.get('office_hour_title')
	start_time = request.POST.get('start_time')
	end_time = request.POST.get('end_time')
	location = request.POST.get('location')
	date = request.POST.get('current-date')
	user_upi = request.POST.get('user-upi')
	module_code = request.POST.get('module-code')
	office_hour = OfficeHours(custom_profile_fk=user_upi, start_time=start_time, end_time=end_time, start_date=date, location=location, title=title, module_code=module_code)
	office_hour.save()
	return HttpResponseRedirect('dashboard/module_details/'+module_code)

def edit_office_hour(request):
	office_hour_id = request.POST.get('office-hour-id')
	module_code = request.POST.get('module-code')
	title = request.POST.get('office_hour_title')
	start_time = request.POST.get('start_time')
	end_time = request.POST.get('end_time')
	location = request.POST.get('location')
	office_hour = OfficeHours.objects.get(pk=office_hour_id)
	office_hour.title = title
	office_hour.start_time = start_time
	office_hour.end_time = end_time
	office_hour.location = location
	office_hour.save()
	return HttpResponseRedirect('dashboard/module_details/'+module_code)

def office_hours_to_dict(office_hours_query_set):
	office_hours_dict_array = []
	for office_hour in office_hours_query_set:
		office_hour_json = {
			'id': office_hour.id,
			'title': office_hour.title,
			'date': str(office_hour.start_date),
			'start': (str(office_hour.start_date) + "T" + office_hour.start_time),
			'end': (str(office_hour.start_date) + "T" + office_hour.end_time),
			'location': office_hour.location
		}
		office_hours_dict_array.append(office_hour_json)
	return office_hours_dict_array
