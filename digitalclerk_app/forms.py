from django import forms

class AdminUploadFileForm(forms.Form):
    file = forms.FileField(label= "Choose excel to upload")