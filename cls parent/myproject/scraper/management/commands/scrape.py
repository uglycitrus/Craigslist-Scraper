import urllib
import re
import datetime

from django.core.management.base import BaseCommand, CommandError

from myproject.scraper.models import Search, Result

class Command(BaseCommand):
	args = 'No arguments'
	help = 'Generates results for all Searches'

	def handle(self, *args, **options):
		"""
		url has to be a craigslist search page
		Craigslistbot scrapes everything that looks like this from a craigslist search page(notice the 1st row is 2tabs in and the rest are 3)
			<p class="row"> 
				<span class="ih" id="images:3kc3ma3l15T65U45P6b2nd02443b2fa601604.jpg">&nbsp;</span> 
				 Feb 23 - <a href="http://newyork.craigslist.org/que/spo/2230781276.html">7'2" al merrick water hog surfboard -</a> 
				 $490<font size="-1"> (astoria)</font> <small class="gc"><a href="/spo/">sporting goods</a></small> <span class="p"> pic</span><br class="c"> 
		
		"""
		for search in Search.objects.all():
			url = search.search_url
			links_list = self.GetLinksList(url)
			scraped_data_master = self.ScrapeOrganizer(links_list)
			result_list = self.GetResultsFromScrapedData(search, scraped_data_master)
			for r in result_list:
				r.save()
			return result_list

	def craigslist_date_to_python_date(self, Mmm_d):
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

	def ScrapeOrganizer(self, links_list):
		"""
		takes a bunch of links from the craigslist scrape
		then returns a list of lists with info on price and images associated with the link
		"""
		scraped_data_master = []
		for i in links_list:
			scraped_data_slave = []
			lines = re.split('\n',i)
			try:
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
			except IndexError:
				pass
		return scraped_data_master


	def GetResultsFromScrapedData(self, search, scraped_data_master):
			result_list = []
			for i in scraped_data_master:
				r = Result()
				r.search = search
				r.status = 'new'
				if i[0] == 'image': r.image = True
				elif i[0] == 'no-image': r.image = False
				r.post_date = self.craigslist_date_to_python_date(i[1])
				r.result_url = i[2]
				r.description = i[3][1:][:-3]
				if i[4] != 'no-price': r.price = int(i[4][1:])
				else: r.price = None
				r.location = i[5]
				result_list.append(r)
			return result_list

	def GetLinksList(self, url):
		file = urllib.urlopen(url, 'r')
		html = file.read()
		file.close()
		links_list = re.findall(r'(?m)^\t\t<p class="row">$\n\t\t\t.*$\n\t\t\t.*$\n\t\t\t.*$', html)
		return links_list
