import urllib
import re
import datetime

from django.db import models
from django.contrib.auth.models import User

class Search(models.Model):
	user = models.ForeignKey(User)
	title = models.CharField("Title", max_length = 200)
	status = models.CharField("Status", max_length = 20, null = True, blank = True)
	frequency = models.DecimalField("Frequency", max_digits = 7, decimal_places = 0)
	search_url = models.CharField("URL", max_length = 200)
	start_date = models.DateField()
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
	

def craigslist_date_to_python_date(Mmm_d):
	year = datetime.date.today().year
	month, day = re.split(' ', Mmm_d)
	month_dict = {'Jan': 1,
		'Feb':2,
		'Mar':3,
		'Apr':4,
		'May':5,
		'Jun':6,
		'Jul':7,
		'Aug':8,
		'Sep':9,
		'Oct':10,
		'Nov':11,
		'Dec':12}
	try:
		month = month_dict[month]
	except:
		raise Mmm_d
	day = int(day)
	return datetime.date(year, month, day)

def hours_to_seconds(frequency_in_hours):
	frequency_in_seconds = frequency_in_hours * 3600
	return frequency_in_seconds

def ScrapeOrganizer(links_list):
	"""
	takes a bunch of links from the craigslist scrape
	then returns a list of lists with info on price and images associated with the link
	"""
	scraped_data_master = []
	for i in links_list:
		scraped_data_slave = []
		lines = re.split('\n',i)
		if re.search('images',lines[1]): scraped_data_slave.append('image')
		else: scraped_data_slave.append('no-image')
		scraped_data_slave.append(re.findall(r'[A-Z][a-z]{2} \d+',lines[2])[0])
		scraped_data_slave.append(re.findall(r'http://.*\.html',lines[2])[0])
		scraped_data_slave.append(re.findall(r'>.*-<',lines[2])[0])
		if re.findall(r'\$\d+',lines[3]): scraped_data_slave.append(re.findall(r'\$\d+',lines[3])[0])
		else: scraped_data_slave.append('no-price')
		if re.findall(r'\(.*\)',lines[3]): scraped_data_slave.append(re.findall(r'\(.*\)',lines[3])[0])
		else:scraped_data_slave.append('no-location')
		scraped_data_master.append(scraped_data_slave)
	return scraped_data_master


def GetResultsFromScrapedData(search, scraped_data_master):
		result_list = []
		for i in scraped_data_master:
			r = Result()
			r.search = search
			r.status = 'new'
			if i[0] == 'image': r.image = True
			elif i[0] == 'no-image': r.image = False
			r.post_date = craigslist_date_to_python_date(i[1])
			r.result_url = i[2]
			r.description = i[3][1:][:-3]
			if i[4] != 'no-price': r.price = int(i[4][1:])
			else: r.price = None
			r.location = i[5]
			result_list.append(r)
		return result_list

def GetLinksList(url):
	file = urllib.urlopen(url, 'r')
	html = file.read()
	file.close()
	links_list = re.findall(r'(?m)^\t\t<p class="row">$\n\t\t\t.*$\n\t\t\t.*$\n\t\t\t.*$', html)
	return links_list

def CraigslistBot(search):
	"""
	url has to be a craigslist search page
	Craigslistbot scrapes everything that looks like this from a craigslist search page(notice the 1st row is 2tabs in and the rest are 3)
			<p class="row"> 
				<span class="ih" id="images:3kc3ma3l15T65U45P6b2nd02443b2fa601604.jpg">&nbsp;</span> 
				 Feb 23 - <a href="http://newyork.craigslist.org/que/spo/2230781276.html">7'2" al merrick water hog surfboard -</a> 
				 $490<font size="-1"> (astoria)</font> <small class="gc"><a href="/spo/">sporting goods</a></small> <span class="p"> pic</span><br class="c"> 
	
	end comments - begin code
	"""
	url = search.search_url
	links_list = GetLinksList(url)
	scraped_data_master = ScrapeOrganizer(links_list)
	result_list = GetResultsFromScrapedData(search, scraped_data_master)
	return result_list

