from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core import serializers
from django.utils import timezone

from .forms import AdminUploadFileForm, AddOfficeHourForm, AddRequestForm
from .helper_classes import MockUserProfile, MockModules
from .models import OfficeHours, Request, Interaction
from .utils import *

import xlrd
import json
import os

# Admin dashboard page (Unintegrated yet)
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
	
# Dashboard home page
def dashboard(request):
	mock_module = MockModules()
	modules_arr = mock_module.listModules
	data = {
		'modules': modules_arr
	}
	return render(request, 'digitalclerk_app/dashboard.html', data)

# Module detail page with CALENDARS and OFFICE HOURS
def module_details(request, module_code):
	user_profile = MockUserProfile()
	user_upi = user_profile.studentProfile1()['upi']
	form = AddOfficeHourForm()
	office_hours = []
	if request.POST.get('lecturer'):
		lecturer_id = request.POST.get('lecturer')
		if(lecturer_id == 'all'):
			office_hours = OfficeHours.objects.filter(module_code=module_code)
		else:
			office_hours = OfficeHours.objects.filter(custom_profile_fk=lecturer_id, module_code=module_code)
	else:
		office_hours = OfficeHours.objects.filter(module_code=module_code)
	office_hours_dict_array = office_hours_to_dict(office_hours)
	office_hours_json = json.dumps(office_hours_dict_array)
	lecturer_list = get_lecturers_for_module(module_code)
	data = {
		'user_upi': user_upi,
		'user_status': user_profile.studentProfile1()['status'],
		'module_code': module_code,
		'form': form,
		'lecturers': lecturer_list,
		'office_hours': office_hours_json
	}
	return render(request, 'digitalclerk_app/module_detail.html',data)

# Office Hours CRUD operations
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

def delete_office_hour(request):
	office_hour_id = request.POST.get('office-hour-id')
	module_code = request.POST.get('module-code')
	office_hour = OfficeHours.objects.get(pk=office_hour_id)
	if office_hour is not None:
		office_hour.delete()
	return HttpResponseRedirect('dashboard/module_details/'+module_code)

# Office hour dashboard for monitoring REQUESTS and INTERACTIONS
def office_hour_dashboard_student(request):
	user_profile = MockUserProfile()
	user_upi = user_profile.studentProfile1()['upi']
	office_hour_id = int(request.GET.get('office-hour-id'))
	lecturer_id = int(request.GET.get('lecturer'))
	request_form = AddRequestForm()
	my_request = None
	prior_request_count = 0
	raised_request = 0
	opened_interaction = 0
	try:
		my_request = Request.objects.get(request_user=user_upi, office_hour_id=office_hour_id, status__in=[1,2])
		try:
			interaction = Interaction.objects.get(request_id=my_request.id)
		except Interaction.DoesNotExist:
			interaction = None
		if my_request:
			prior_request_count = get_prior_requests_count(my_request.id)
			raised_request = 1
		if interaction:
			opened_interaction = 1
	except Request.DoesNotExist:
		my_request = None
	data = {
		'user_upi': user_upi,
		'office_hour_id': office_hour_id,
		'lecturer_id': lecturer_id,
		'lecturer': user_profile.getNameFromId(lecturer_id),
		'request_form': request_form,
		'my_request': my_request,
		'raised_request': raised_request,
		'opened_interaction': opened_interaction,
		'prior_request_count': prior_request_count
	}
	return render(request, 'digitalclerk_app/office_hour_dashboard_student.html', data)

def office_hour_dashboard(request):
	user_profile = MockUserProfile()
	user_upi = user_profile.lecturerProfile()['upi']
	office_hour_id = int(request.GET.get('office-hour-id'))
	lecturer_id = int(request.GET.get('lecturer'))
	open_requests = format_requests(Request.objects.filter(office_hour_id=office_hour_id, status=1).order_by('time_raised'))
	closed_requests = format_interactions(Interaction.objects.filter(office_hour_id=office_hour_id, status__in=[1,2]).order_by('-time_closed'))
	open_interactions = format_interactions(Interaction.objects.filter(office_hour_id=office_hour_id, status=0).order_by('time_opened'))
	data = {
		'user_upi': user_upi,
		'user_status': user_profile.lecturerProfile()['status'],
		'office_hour_id': office_hour_id,
		'lecturer_id': lecturer_id,
		'lecturer': user_profile.getNameFromId(lecturer_id),
		'open_requests': open_requests,
		'closed_requests': closed_requests,
		'open_interactions': open_interactions
	}
	return render(request, 'digitalclerk_app/office_hour_dashboard.html', data)

# REQUEST CRUD operations
def add_request(request, office_hour_id, user_id, lecturer_id):
	request_title = request.POST.get('request_title')
	request_description = request.POST.get('request_description')
	tried_solutions = request.POST.get('tried_solutions')
	help_request = Request(office_hour_id=office_hour_id,
		request_user=user_id,
		lecturer=lecturer_id,
		time_raised=timezone.now(),
		request_title=request_title,
		request_description=request_description,
		tried_solutions=tried_solutions
	)
	help_request.save()
	return HttpResponseRedirect('/office_hour_dashboard_student?office-hour-id='+ office_hour_id + '&lecturer=' + lecturer_id)

def edit_request(request, office_hour_id, lecturer_id, help_request_id):
	help_request = Request.objects.get(pk=help_request_id)
	help_request.request_title = request.POST.get('request_title')
	help_request.request_description = request.POST.get('request_description')
	help_request.tried_solutions = request.POST.get('tried_solutions')
	help_request.save()
	return HttpResponseRedirect('/office_hour_dashboard_student?office-hour-id='+ office_hour_id + '&lecturer=' + lecturer_id)

def close_request(request, office_hour_id, lecturer_id, help_request_id):
	help_request = Request.objects.get(pk=help_request_id)
	if help_request is not None:
		help_request.delete()
	return HttpResponseRedirect('/office_hour_dashboard_student?office-hour-id='+ office_hour_id + '&lecturer=' + lecturer_id)

# INTERACTION operations
def open_interaction(request, office_hour_id, lecturer_id, help_request_id, status):
	help_request = Request.objects.get(pk=help_request_id)
	help_request.status = 2
	help_request.save()
	interaction = Interaction(lecturer=lecturer_id,
		time_opened=timezone.now(),
		time_closed=None,
		status=status,
		office_hour_id=office_hour_id,
		request_id=help_request_id
	)
	print("Status -----------" + status)
	if (status == '2'):
		print("Status is 2")
		help_request.status = 0
		interaction.time_closed = timezone.now()
		help_request.save()
	interaction.save()
	return HttpResponseRedirect('/office_hour_dashboard?office-hour-id='+ office_hour_id + '&lecturer=' + lecturer_id)

def close_interaction(request, office_hour_id, lecturer_id, help_request_id, interaction_id, status):
	help_request = Request.objects.get(pk=help_request_id)
	help_request.status = 0
	help_request.save()
	interaction = Interaction.objects.get(pk=interaction_id)
	interaction.time_closed = timezone.now()
	interaction.status = status
	interaction.save()
	return HttpResponseRedirect('/office_hour_dashboard?office-hour-id='+ office_hour_id + '&lecturer=' + lecturer_id)

