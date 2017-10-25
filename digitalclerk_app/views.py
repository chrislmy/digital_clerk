from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect


from .forms import AdminUploadFileForm

import xlrd
import json

# Create your views here.
def dashboard(request):
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

def office(request):
	office_hours = [{
					'id': '1',
					'title': 'All Day Office Hour',
					'start': '2017-10-25',
				},
				{
					'id': '2',
					'title': 'Office Hour',
					'start': '2017-10-17T16:00:00'
				},
				{
					'id': '3',
					'title': 'Office Hour Extra',
					'start': '2017-10-12T10:30:00',
					'end': '2017-10-12T12:30:00'
				}]
	office_hours_json = json.dumps(office_hours)
	print(type(office_hours_json))
	data = {
		'office_hours':office_hours_json
	}
	return render(request, 'digitalclerk_app/office.html',data)