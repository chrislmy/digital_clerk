from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.core import serializers
from django.core.mail import send_mail
from django.utils import timezone

from .forms import AdminUploadFileForm, AddOfficeHourForm, AddRequestForm, FeedbackForm
from .helper_classes import MockUserProfile, MockModules
from .models import OfficeHours, Request, Interaction, Feedback
from .utils import *
from .endpoints import *

import xlrd
import json
import os
import requests

# UCL API Oauth2.0 login
def render_login_home(request):
	return render(request, 'digitalclerk_app/login_home.html')

def process_logout(request):
	del request.session['token_code']
	return HttpResponseRedirect('login_home')

def process_login(request):
	state = generate_state()
	request.session["state"] = state
	auth_url = settings.UCLAPI_URL + "/oauth/authorise"
	auth_url += "?client_id=" + settings.UCLAPI_CLIENT_ID
	auth_url += "&state=" + state
	return redirect(auth_url)

def oauth_callback(request):
	try:
		result = request.GET.get("result")
	except KeyError:
		return JsonResponse({"error": "No result parameter passed."})
	if result == "allowed":
		return allowed(request)
	elif result == "denied":
		return denied(request)
	else:
		return JsonResponse({"ok": False, "error": "Result was not allowed or denied."})

def allowed(request):
	try:
		code = request.GET.get("code")
		client_id = request.GET.get("client_id")
		state = request.GET.get("state")
	except KeyError:
		return JsonResponse({
			"error": "Parameters missing from request."
		})
	url = settings.UCLAPI_URL + "/oauth/token"
	params = {
		'grant_type': 'authorization_code',
		'client_id': client_id,
		'code': code,
		'client_secret': settings.UCLAPI_CLIENT_SECRET
	}
	oauth_token = requests.get(url, params=params)
	try:
		token_data = oauth_token.json()
		if token_data["ok"] is not True:
			return JsonResponse({
				"ok": False,
				"error": "An error occurred: " + token_data["error"]
			})
		if token_data["state"] != state:
			return HttpResponseRedirect('login_home')
		if token_data["client_id"] != client_id:
			return HttpResponseRedirect('login_home')
		token_code = token_data["token"]
		scope_data = json.loads(token_data["scope"])
		request.session["token_code"] = token_code
		store_user(token_code)
	except KeyError as e:
		print(e)
		return HttpResponseRedirect('login_home')
	return HttpResponseRedirect('dashboard_test')


def denied(request):
	request.session["token_code"] = settings.SESSION_TOKEN_LOGGED_OUT
	print('denied!')
	return HttpResponseRedirect('login_home')

# Admin dashboard page (Unintegrated yet)
def admin_index(request):
	if request.method == 'POST':
		form = AdminUploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			inputFile = request.FILES['file']
			data = parse_input_file(inputFile)
			return render(request, 'digitalclerk_app/uploaded.html', data)
	else:
		form = AdminUploadFileForm()
	return render(request, 'digitalclerk_app/admin-upload.html', {'form': form})
	
def dashboard_test(request):
	url = settings.UCLAPI_URL + "/oauth/user/data"
	params = {
		'token': request.session["token_code"],
		'client_secret': settings.UCLAPI_CLIENT_SECRET
	}
	user_data = requests.get(url, params=params)
	modules_arr = getPersonalModules(request.session['token_code'])
	print(modules_arr)
	data = {
		'user_data': user_data.json(),
		'modules': modules_arr,
	}
	return render(request, 'digitalclerk_app/dashboard_test.html', data)

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
	user_upi = 0
	user_status = 'none'
	if(settings.MODULE_DETAIL_DASHBOARD_PROFILE == 'LECTURER_PROFILE'):
		user_upi = user_profile.lecturerProfile()['upi']
		user_status = user_profile.lecturerProfile()['status']
	elif(settings.MODULE_DETAIL_DASHBOARD_PROFILE == 'ASSISTANT_PROFILE'):
		user_upi = user_profile.assistantProfile()['upi']
		user_status = user_profile.assistantProfile()['status']
	elif(settings.MODULE_DETAIL_DASHBOARD_PROFILE == 'STUDENT_PROFILE_1'):
		user_upi = user_profile.studentProfile1()['upi']
		user_status = user_profile.studentProfile1()['status']
	elif(settings.MODULE_DETAIL_DASHBOARD_PROFILE == 'STUDENT_PROFILE_2'):
		user_upi = user_profile.studentProfile2()['upi']
		user_status = user_profile.studentProfile2()['status']
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
		'user_status': user_status,
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
	user_upi = 0;
	if(settings.OFFICE_HOUR_DASHBOARD_STUDENT_PROFILE == 'STUDENT_PROFILE_1'):
		user_upi = user_profile.studentProfile1()['upi']
	elif(settings.OFFICE_HOUR_DASHBOARD_STUDENT_PROFILE == 'STUDENT_PROFILE_2'):
		user_upi = user_profile.studentProfile2()['upi']
	office_hour_id = int(request.GET.get('office-hour-id'))
	office_hour = OfficeHours.objects.get(pk=office_hour_id)
	lecturer_id = int(request.GET.get('lecturer'))
	my_request = None
	prior_request_count = 0
	past_requests = format_requests(Request.objects.filter(office_hour_id=office_hour_id, request_user=user_upi, status=0).order_by('-time_raised'))
	raised_request = 0
	opened_interaction = 0
	try:
		my_request = Request.objects.get(request_user=user_upi, office_hour_id=office_hour_id, status__in=[1,2])
		try:
			interaction = Interaction.objects.get(request_id=my_request.id)
		except Interaction.DoesNotExist:
			interaction = None
		if my_request:
			prior_request_count = get_prior_requests_count(office_hour_id, my_request.id)
			raised_request = 1
		if interaction:
			opened_interaction = 1
	except Request.DoesNotExist:
		my_request = None
	data = {
		'user_upi': user_upi,
		'office_hour_id': office_hour_id,
		'lecturer_id': lecturer_id,
		'office_hour': office_hour,
		'lecturer': user_profile.getNameFromId(lecturer_id),
		'request_form': AddRequestForm(),
		'my_request': my_request,
		'raised_request': raised_request,
		'opened_interaction': opened_interaction,
		'prior_request_count': prior_request_count,
		'office_hour_is_over': office_hours_is_over(office_hour_id),
		'past_requests': past_requests
	}
	return render(request, 'digitalclerk_app/office_hour_dashboard_student/index.html', data)

def refresh_request_form(request):
	user_upi = int(request.GET.get('user-upi'))
	office_hour_id = int(request.GET.get('office-hour-id'))
	lecturer_id = int(request.GET.get('lecturer'))
	prior_request_count = 0
	my_request = None
	opened_interaction = 0
	raised_request = 0
	try:
		my_request = Request.objects.get(request_user=user_upi, office_hour_id=office_hour_id, status__in=[1,2])
		try:
			interaction = Interaction.objects.get(request_id=my_request.id)
		except Interaction.DoesNotExist:
			interaction = None
		if my_request:
			prior_request_count = get_prior_requests_count(office_hour_id, my_request.id)
			raised_request = 1
		if interaction:
			opened_interaction = 1
	except Request.DoesNotExist:
		my_request = None
	data = {
		'user_upi': user_upi,
		'office_hour_id': office_hour_id,
		'lecturer_id': lecturer_id,
		'my_request': my_request,
		'request_form': AddRequestForm(),
		'my_request': my_request,
		'raised_request': raised_request,
		'opened_interaction': opened_interaction,
		'prior_request_count': prior_request_count,
		'office_hour_is_over': office_hours_is_over(office_hour_id),
	}
	return render(request, 'digitalclerk_app/office_hour_dashboard_student/refresh_request_form.html', data)

def refresh_past_requests(request):
	user_upi = int(request.GET.get('user-upi'))
	office_hour_id = int(request.GET.get('office-hour-id'))
	past_requests = format_requests(Request.objects.filter(office_hour_id=office_hour_id, request_user=user_upi, status=0).order_by('-time_raised'))
	data = {
		'past_requests': past_requests
	}
	return render(request, 'digitalclerk_app/office_hour_dashboard_student/refresh_past_requests.html', data)

def office_hour_dashboard(request):
	user_profile = MockUserProfile()
	user_upi = 0
	user_status = 'none'
	if(settings.OFFICE_HOUR_DASHBOARD_STAFF_PROFILE == 'LECTURER_PROFILE'):
		user_upi = user_profile.lecturerProfile()['upi']
		user_status = user_profile.lecturerProfile()['status']
	elif(settings.OFFICE_HOUR_DASHBOARD_STAFF_PROFILE == 'ASSISTANT_PROFILE'):
		user_upi = user_profile.assistantProfile()['upi']
		user_status = user_profile.assistantProfile()['status']
	office_hour_id = int(request.GET.get('office-hour-id'))
	office_hour = OfficeHours.objects.get(pk=office_hour_id)
	lecturer_id = int(request.GET.get('lecturer'))
	open_requests = format_requests(Request.objects.filter(office_hour_id=office_hour_id, status=1).order_by('time_raised'))
	latest_open_request_id = 0
	if(len(open_requests) != 0):
		latest_open_request = open_requests[0]
		latest_open_request_id = latest_open_request['request'].id
	closed_requests = format_interactions(Interaction.objects.filter(office_hour_id=office_hour_id, status__in=[1,2]).order_by('-time_closed'))
	open_interactions = format_interactions(Interaction.objects.filter(office_hour_id=office_hour_id, status=0).order_by('time_opened'))
	data = {
		'user_upi': user_upi,
		'user_status': user_status,
		'office_hour_id': office_hour_id,
		'lecturer_id': lecturer_id,
		'lecturer': user_profile.getNameFromId(lecturer_id),
		'open_requests': open_requests,
		'latest_open_request_id': latest_open_request_id,
		'closed_requests': closed_requests,
		'open_interactions': open_interactions,
		'office_hour': office_hour,
		'form': FeedbackForm()
	}
	return render(request, 'digitalclerk_app/office_hour_dashboard_staff/index.html', data)

def refresh_open_requests(request):
	office_hour_id = int(request.GET.get('office-hour-id'))
	open_requests = format_requests(Request.objects.filter(office_hour_id=office_hour_id, status=1).order_by('time_raised'))
	lecturer_id = int(request.GET.get('lecturer'))
	data = {
		'open_requests': open_requests,
		'office_hour_id': office_hour_id,
		'lecturer_id': lecturer_id,
		'form': FeedbackForm()
	}
	return render(request, 'digitalclerk_app/office_hour_dashboard_staff/refresh_open_requests.html', data)

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
def open_interaction(request, office_hour_id, lecturer_id, help_request_id, status, has_feedback):
	help_request = Request.objects.get(pk=help_request_id)
	office_hour = OfficeHours.objects.get(pk=office_hour_id)
	user_profile = MockUserProfile()
	lecturer_name = user_profile.getNameFromId(int(lecturer_id))
	user_name = user_profile.getNameFromId(help_request.request_user)
	user_email = user_profile.getEmailFromId(help_request.request_user)
	subject = "Digital Clerk - Interaction Opened!"
	email_message = 'Hello ' + user_name + ',\n\n' 
	email_message += lecturer_name + ' has opened an interaction for one of your requests in the office hour "' 
	email_message += office_hour.title + '".\n' 
	email_message += 'The office hour is from ' + office_hour.start_time + ' to ' + office_hour.end_time
	send_mail(subject, email_message, settings.EMAIL_HOST_USER, [user_email], fail_silently=False)
	help_request.status = 2
	help_request.save()
	interaction = Interaction(lecturer=lecturer_id,
		time_opened=timezone.now(),
		time_closed=None,
		status=status,
		office_hour_id=office_hour_id,
		request_id=help_request_id
	)
	if (status == '2'):
		if(has_feedback == '1'):
			next_steps = request.POST.get('next_steps')
			foot_note = request.POST.get('foot_note')
			feedback = Feedback(lecturer=lecturer_id, next_steps=next_steps, foot_note=foot_note, request_id=help_request_id)
			feedback.save()
		help_request.status = 0
		interaction.time_closed = timezone.now()
		help_request.save()
	interaction.save()
	return HttpResponseRedirect('/office_hour_dashboard?office-hour-id='+ office_hour_id + '&lecturer=' + lecturer_id)

def close_interaction(request, office_hour_id, lecturer_id, help_request_id, interaction_id, status, has_feedback):
	if(has_feedback == '1'):
		next_steps = request.POST.get('next_steps')
		foot_note = request.POST.get('foot_note')
		feedback = Feedback(lecturer=lecturer_id, next_steps=next_steps, foot_note=foot_note, request_id=help_request_id)
		feedback.save()
	help_request = Request.objects.get(pk=help_request_id)
	help_request.status = 0
	help_request.save()
	interaction = Interaction.objects.get(pk=interaction_id)
	interaction.time_closed = timezone.now()
	interaction.duration_seconds = get_time_difference_seconds(interaction.time_opened, interaction.time_closed)
	interaction.status = status
	interaction.save()
	return HttpResponseRedirect('/office_hour_dashboard?office-hour-id='+ office_hour_id + '&lecturer=' + lecturer_id)
