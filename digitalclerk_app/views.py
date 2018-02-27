from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.core import serializers
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


from .forms import AdminUploadFileForm, AddOfficeHourForm, AddRequestForm, FeedbackForm
from .helper_classes import MockUserProfile, MockModules
from .models import OfficeHours, Request, Interaction, Feedback, HelpStaff, UserProfile
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
	return HttpResponseRedirect('login')

def process_logout_admin(request):
	logout(request)
	return HttpResponseRedirect('login_home')

def process_login(request):
	state = generate_state()
	request.session["state"] = state
	auth_url = settings.UCLAPI_URL + "/oauth/authorise"
	auth_url += "?client_id=" + settings.UCLAPI_CLIENT_ID
	auth_url += "&state=" + state
	return redirect(auth_url)

def process_login_admin(request):
	username = request.POST.get('username')
	password = request.POST.get('password')

	if username is None or password is None:
		return HttpResponseRedirect('login_home')
	else:
		user = auth.authenticate(username=username, password=password)
		if user is not None:
			auth.login(request, user)
			return HttpResponseRedirect('admin_index')
		else:
			return HttpResponseRedirect('login_home')

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
		return HttpResponseRedirect('login_home')
	return HttpResponseRedirect('dashboard')


def denied(request):
	request.session["token_code"] = settings.SESSION_TOKEN_LOGGED_OUT
	print('denied!')
	return HttpResponseRedirect('login_home')

# Admin dashboard page
def admin_index(request):
	if request.user.is_authenticated:
		table_entries = get_help_staff()
		if request.method == 'POST':
			form = AdminUploadFileForm(request.POST, request.FILES)
			if form.is_valid():
				inputFile = request.FILES['file']
				excel_data = parse_input_file(inputFile)
				uploaded_msg = "Excel file successfully uploaded!"
				table_entries = get_help_staff()
				data = {
					'form': form,
					'uploaded_msg': uploaded_msg,
					'excel_data': excel_data,
					'table_entries':table_entries
				}
				return render(request, 'digitalclerk_app/admin-upload.html', data)
		else:
			form = AdminUploadFileForm()

		data = {
			'form': form,
			'uploaded msg': None,
			'excel_data': None,
			'table_entries': table_entries
		}
		return render(request, 'digitalclerk_app/admin-upload.html', data)
	else:
		return HttpResponseRedirect('login_home')

# Dashboard home page
def dashboard(request):
	auth_token = request.session['token_code']
	user_data = get_user_details(auth_token)
	user_upi = user_data['upi']
	user = None
	modules_arr = []
	try:
		help_staff = HelpStaff.objects.get(upi=user_upi)
		user = UserProfile.objects.get(upi=user_upi)
		user.status = 'Lecturer'
		user.save()
	except HelpStaff.MultipleObjectsReturned:
		user = UserProfile.objects.get(upi=user_upi)
		user.status = 'Lecturer'
		user.save()
	except HelpStaff.DoesNotExist:
		user = UserProfile.objects.get(upi=user_upi)
		user.status = 'Student'
		user.save()
	if (user.status == 'Student'):		
		modules_arr = getPersonalModules(auth_token)
	else:
		modules_arr = getStaffModules(user_upi)
	data = {
		'user_data': user_data,
		'modules': modules_arr,
	}
	return render(request, 'digitalclerk_app/dashboard.html', data)

# Profile page
def profile_page(request):
	auth_token = request.session['token_code']
	user_data = get_user_details(auth_token)
	modules_arr = []
	num_modules = len(modules_arr)
	interactions = None
	interaction_report = None;
	if(user_data['status'] != 'Student'):
		interactions = Interaction.objects.filter(lecturer=user_data['id'],status=1)
		resolved_interactions = len(interactions)
		interactions = Interaction.objects.filter(lecturer=user_data['id'],status=0)
		abandoned_interactions = len(interactions)
		interactions = Interaction.objects.filter(lecturer=user_data['id'])
		total_time = 0
		total_interactions = len(interactions)
		for interaction in interactions:
			total_time += interaction.duration_seconds
		total_time_avg = int(total_time / total_interactions)
		total_minutes, total_seconds = divmod(total_time, 60)
		total_minutes_avg, total_seconds_avg = divmod(total_time_avg, 60)
		interaction_report = {
			'total_interactions': total_interactions,
			'resolved_interactions': resolved_interactions,
			'abandoned_interactions': abandoned_interactions,
			'total_time_minutes': total_minutes,
			'total_time_seconds': total_seconds,
			'total_time_minutes_avg': total_minutes_avg,
			'total_time_seconds_avg': total_seconds_avg,
		}
		modules_arr = getStaffModules(user_data['upi'])
	else:
		modules_arr = getPersonalModules(auth_token)
	data = {
		'user_data': user_data,
		'modules': modules_arr,
		'num_modules': num_modules,
		'interaction_report': interaction_report
	}
	return render(request, 'digitalclerk_app/profile.html', data)

# Module detail page with CALENDARS and OFFICE HOURS
def module_details(request, module_code):
	auth_token = request.session['token_code']
	user_profile = get_user_details(auth_token)
	user_upi = int(user_profile['id'])
	user_status = user_profile['status']
	module_name = None
	user_enrolled = False
	if (user_status == 'Student'):	
		module_name = get_module_name(module_code, user_status)
		user_enrolled = user_is_enrolled(user_upi, module_code)
	else:
		module_name = get_module_name(module_code, user_status)
		user_enrolled = staff_is_enrolled(user_profile['upi'], module_code)
	num_office_hours = get_module_num_active_office_hours(module_code)
	num_students_enrolled = get_num_students_in_module(module_code)

	form = AddOfficeHourForm()
	office_hours = []
	office_hours_json = None
	lecturer_list = None
	module_staff = get_module_staff(module_code)
	if user_enrolled == True:
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
		'user_is_enrolled': user_enrolled,
		'module_code': module_code,
		'module_name': module_name,
		'module_staff': module_staff,
		'num_office_hours': num_office_hours,
		'num_students_enrolled': num_students_enrolled,
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
	recurring_times = request.POST.get('recurring_times')
	user_upi = request.POST.get('user-upi')
	module_code = request.POST.get('module-code')
	start_date = datetime.datetime.strptime(date, "%Y-%m-%d")
	for x in range(0,int(recurring_times)):
		date_str = start_date.strftime("%Y-%m-%d")
		office_hour = OfficeHours(custom_profile_fk=user_upi, start_time=start_time, end_time=end_time, start_date=date_str, location=location, title=title, module_code=module_code)
		office_hour.save()
		start_date = start_date + datetime.timedelta(days=7)
		
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
	auth_token = request.session['token_code']
	user_profile = get_user_details(auth_token)
	user_upi = user_profile['id']
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
		'lecturer': get_user_full_name(lecturer_id),
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
	auth_token = request.session['token_code']
	user_profile = get_user_details(auth_token)
	user_upi = user_profile['id']
	user_status = user_profile['status']

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
		'lecturer':get_user_full_name(lecturer_id),
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
	user_fullname = get_user_full_name(help_request.request_user)
	lecturer_name = get_user_full_name(lecturer_id)
	user_email = get_user_email(help_request.request_user)

	subject = "Digital Clerk - Interaction Opened!"
	email_message = 'Hello ' + user_fullname + ',\n\n' 
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
