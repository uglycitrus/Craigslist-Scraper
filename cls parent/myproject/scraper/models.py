import urllib
import re
import datetime

from django.db import models
from django.contrib.auth.models import User

class Search(models.Model):
	user = models.ForeignKey(User)
	title = models.CharField("Title", max_length = 200)
	status = models.CharField("Status", max_length = 20, null = True, blank = True)
	search_url = models.CharField("URL", max_length = 200)
	start_date = models.DateField(auto_now=True)
	end_date = models.DateField(null = True, blank = True)

#	class Meta:
#		ordering = 'start_date'

	def __unicode__(self):
		return self.title

	def save(self):
		"""
		DO NOT SAVE SEARCHES THAT SCRAPE THE SAME URL
		"""
		try:
			obj = Search.objects.get(
				search_url = self.search_url
				)
			saved = False
		except Search.DoesNotExist:
			super(Search, self).save()
			saved = True
		return self, saved
	


class Result(models.Model):
	search = models.ForeignKey(Search)
	status = models.CharField("Status", max_length = 20, null = True, blank = True)
	description = models.CharField("Description", max_length = 70)
	price = models.DecimalField("Price", max_digits = 7, decimal_places = 0, null = True, blank = True)
	result_url = models.CharField("URL", max_length = 200)
	image = models.BooleanField()
	location = models.CharField("Location", max_length = 40, null = True, blank = True)
	post_date = models.DateField()
	
#	class Meta:
#		ordering = ('post_date')

	def __unicode__(self):
		return self.description+' : $'+str(self.price)

	def save(self):
		"""
		DO NOT SAVE IDENTICAL RESULTS FOR THE SAME SEARCH 
		"""
		try:
			obj = Result.objects.get(
				search = self.search, 
				status = self.status, 
				description = self.description, 
				price = self.price, 
				result_url = self.result_url, 
				image = self.image, 
				location = self.location, 
				post_date = self.post_date, 
				)
		except Result.DoesNotExist:
			super(Result, self).save()
		return self
	


