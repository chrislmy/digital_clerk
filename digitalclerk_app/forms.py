from django import forms

class AdminUploadFileForm(forms.Form):
	file = forms.FileField()

class AddOfficeHourForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(AddOfficeHourForm, self).__init__(*args, **kwargs)
		choices = []
		for x in range(1,31):
			field_str = str(x) + ' weeks'
			choices.append((x,field_str))
		self.fields['recurring_times'].choices = choices

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
	recurring_times = forms.ChoiceField(choices=())
	office_hour_title = forms.CharField(initial="")

class AddRequestForm(forms.Form):
	request_title = forms.CharField(max_length=150)
	request_description = forms.CharField(widget=forms.Textarea(attrs = {"rows":5, "cols":80}))
	tried_solutions = forms.CharField(widget=forms.Textarea(attrs = {"rows":5, "cols":80}))

class FeedbackForm(forms.Form):
	next_steps = forms.CharField(required=False, widget=forms.Textarea(attrs = {"rows":5, "cols":80}))
	foot_note = forms.CharField(required=False, widget=forms.Textarea(attrs = {"rows":5, "cols":80}))