from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

from cls.scraper.models import Search

class LogInForm(forms.Form):
	username = forms.CharField()
	password = forms.CharField(widget = forms.PasswordInput)

class SearchEditForm(ModelForm):
	class Meta:
		model = Search
		exclude = ('user', 'start_date', 'end_date')

class UserEditForm(ModelForm):
	class Meta:
		model = User
		fields = ('username','first_name', 'last_name', 'email')
