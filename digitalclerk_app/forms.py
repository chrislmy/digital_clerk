from django import forms

class AdminUploadFileForm(forms.Form):
    file = forms.FileField(label= "Choose excel to upload")

class AddOfficeHourForm(forms.Form):
	TIMES = (('09:00', '09:00'),
		('09:30', '09:30'),
		('10:00', '10:00'),
		('10:30','10:30'),
		('11:00','11:00'),
		('11:30','11:30'),
		('12:00','12:00'),
		('12:30','12:30'),
		('13:00','13:00'),
		('13:30','13:30'),
		('14:00','14:00'),
		('14:30','14:30'),
		('15:00','15:00'),
		('15:30','15:30'),
		('16:00','16:00'),
		('16:30','16:30'),
		('17:00','17:00'),
		('17:30','17:30'),
		('18:00','18:00'))
	start_time = forms.ChoiceField(choices=TIMES)
	end_time = forms.ChoiceField(choices=TIMES)
	location = forms.CharField()
	office_hour_title = forms.CharField(initial="")