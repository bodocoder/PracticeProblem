from django.shortcuts import render
from django.core.paginator import Paginator
import pickle
import requests as rq
import json

suff = '?offset={}&sortBy=problemName&sortOrder=asc'
headers = {
	'Authorization':'Bearer ',
	'content-Type':'application/json'
}

api_endpoint = 'https://api.codechef.com/'
redirect_uri = 'http://localhost:8000/'

access_token_endpoint = 'https://api.codechef.com/oauth/token'


def refresh_token(data):
	file = open('keys','wb')
	headers ={'grant_type':'refresh_token',
			'refresh_token':data['refresh_token'],'client_id':data['client_id']
			,'client_secret':data['client_secret'],
			'content-Type':'application/json'
	}
	res = rq.request("POST",access_token_endpoint,data=headers).json()['result']['data']
	data['access_token'] = res['access_token']
	data['refresh_token'] = res['refresh_token']
	pickle.dump(data,file)
	file.close()
	return data


def getData():
	file = open('keys','rb')
	data = pickle.load(file)
	file.close()
	return data
def make_req(url,data):
	headers['Authorization']='Bearer '+data['access_token']
	res = rq.get(url,headers=headers).json()
	return res
def app_home(requests):
	dlevel = 'easy'
	#sel_level = {'easy':'false','school':'false','medium':'false','hard':'false'}
	url = api_endpoint + 'problems/'+dlevel+suff.format(1)
	if 'difficulty' in requests.GET:
		dlevel = requests.GET['difficulty']
		url = api_endpoint + 'problems/'+dlevel+suff.format(1)
	data = getData()
	res = make_req(url,data)

	if res['status'] == 'OK':
		res=res['result']['data']['content']
	else:
		data = refresh_token(data)
		res = make_req(url, data)['result']['data']['content']

	paginator = Paginator(res,20)
	page_number = 1
	if 'page' in requests.GET:
		page_number	= int(requests.GET['page'])
	page_obj = paginator.get_page(page_number)
	tags = ['2-d', '2-d-array', '2-d-prefixsum', '2-sat']
	purls = {
		'next_page':'?difficulty='+dlevel+'&'+'page='+str(page_number+1),
		'first_page':'?difficulty='+dlevel+'&'+'page='+str(1),
		'prev_page':'?difficulty='+dlevel+'&'+'page='+str(page_number-1),
		'last_page':'?difficulty='+dlevel+'&'+'page='+str(paginator.num_pages)
	}
	return render(requests,"app/layout.html",{'page_obj':page_obj,'tags':tags,'purls':purls})


def problem_detail(request,pcode):
	return render(request,'app/problemDetail.html')