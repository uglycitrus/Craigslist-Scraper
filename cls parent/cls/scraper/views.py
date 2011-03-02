
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse

from cls.scraper.models import Search
from cls.scraper.models import Result

from cls.scraper.forms import SearchEditForm
from cls.scraper.forms import UserEditForm
from cls.scraper.forms import LogInForm

def login_view(request):
	# forward the user to the welcome page if they are logged in
	if request.user.is_authenticated():
		return HttpResponseRedirect( reverse('search_list') )
	# if they're not logged in already they must complete the sign in form
	form = LogInForm()
	if request.method == 'POST':
		form = LogInForm(request.POST)
		if form.is_valid():
			username = request.POST.get('username')
			password = request.POST.get('password')
			user = authenticate(username = username, password = password)
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('search_list'))
			else:
				raise "Account is disabled"
				return render_to_response('login.html', {'form':form, 'user':user})
		else:
			return render_to_response('login.html', {'form':form})
	else:
		return render_to_response('login.html', {'form':form})

def logout_view(request):
	logout(request)
	return HttpResponseRedirect( reverse('login'))

@login_required
def search_list(request):
	user = request.user
	list = Search.objects.all()	
	return render_to_response('search_list.html', {'list':list, 'user':user})

@login_required
def result_list(request, id):
	search = get_object_or_404(Search, id = id)
	user = request.user
	list = search.result_set.all()
	graph = []
	count = 0
	for i in list:
		count = count + 1
		if i.price: graph.append([count ,int(i.price)])
	return render_to_response('result_list.html', {'list':list, 'user':user, 'graph':graph})

@login_required
def search_new(request):
	user = request.user
	form = SearchEditForm()
	if request.method == 'POST':
		form = SearchEditForm(request.POST)
		if form.is_valid():
			search = SearchEditFormHandler(form)
			
	return render_to_response('form.html', {'form':form, 'user':user})

@login_required
def user_edit(request):
	user = request.user
	form = UserEditForm()
	return render_to_response('form.html', {'form':form, 'user':user})

def SearchEditFormHandler(form):
	search = Search()

