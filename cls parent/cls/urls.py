import os

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('cls.scraper.views',
	url(r'^accounts/login/$', 'login_view', name = 'login'),
	url(r'^accounts/logout/$', 'logout_view', name = 'logout'),
	url(r'^accounts/edit/$', 'user_edit', name = 'user_edit'),
	url(r'^search/$', 'search_list', name = 'search_list'),
	url(r'^search/new/$', 'search_new', name = 'search_new'),
	url(r'^results/(?P<id>\d+)/$', 'result_list', name = 'result_list'),
	
	# Example:
	# (r'^cls/', include('cls.foo.urls')),

	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0]+'/static_media'}),
    )

