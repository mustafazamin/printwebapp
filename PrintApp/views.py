import json
import os
from os import path
from os.path import pathsep

import requests
from django.conf.global_settings import MEDIA_ROOT
from django.contrib import messages
from django.contrib.auth.models import auth
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from MySQLdb.constants.ER import USERNAME
from octorest import OctoRest
from urllib3.connectionpool import HTTPConnectionPool
from starprint.settings import MEDIA_URL

url = "http://192.168.1.53"
apikey = ''


client = OctoRest(url="http://192.168.1.53", apikey="EB9B26499B6E49609D1EF1C1A6680985")
state = client.state()

def make_client(url, apikey):
    
    try:
        client = OctoRest(url=url, apikey=apikey)
        return client
    except ConnectionError as ex:
         # Handle exception as you wish
        print('Connection time-out!')


def login(request):

    if request.user.is_authenticated:
        auth.login(request, request.user)
        return redirect('Home')

    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            try:
                
                url1 = f"{url}/api/login?user={username}&pass={password}"
                response = requests.post(url1)
                result = response.json()
                global apikey
                apikey = result.get('apikey')
                print(apikey)
                auth.login(request, user)
                return redirect('Home')
            
            except ConnectionError:
                messages.info(request, 'Connection timeout... Try again!')
        else:
            messages.error(request,'Invalid Credentials... Try again!')
            return redirect('login')
    return render(request, 'index.html')


def Home(request):
    #url = f"http://192.168.1.53/api/connection?apikey={apikey}"
    #res = requests.get(url)
    #response = res.json()
    #state = response.get('current').get('state')
    #print(str(state)
    
    return render(request, 'Home.html', {'state': state, 'apikey':apikey})


def connect(request):
    client.connect()
    return redirect('Home')

global sizeformat
sizeformat={ 1 :' KB', 2 : ' MB', 3 : ' GB'}
def GetFiles(request):
    fileresponse = requests.get(f"http://192.168.1.53/api/files?apikey={apikey}")
    fileresponse = fileresponse.json()
    data = fileresponse.get('files')
    fdata = list()
    for item in data:
        size = int(item.get('size'))
        count = 0
        while size >=1024:
            size = round(size/1024, 2)
            count+=1
        size=str(size)+sizeformat.get(count)
        tmp = {'Name':item.get('name'), 'Origin':item.get('origin'), 'Size':size,  'Type':item.get('type'), 'Download':str(item.get('refs').get('download')) + f"?apikey={apikey}"}
        fdata.append(tmp)

    return render(request,'files.html', {'fdata':fdata})


def disconnect(request):
    client.disconnect()
    return redirect('Home')

def home_coming(request):
    client.home()
    return redirect('Home')
    

def select(request):
    payload = { 'command': 'select'}
    headers = {'content-type': 'application/json'}
    res = requests.post(f"http://192.168.1.53/api/files/local/a.gcode?apikey={apikey}",json=payload, headers=headers)
    if res.status_code is 204:
        messages.info(request,'File selected!!!')
    return redirect('Home')

def start(request):
    payload = { 'command': 'start'}
    headers = {'content-type': 'application/json'}
    res = requests.post(f"http://192.168.1.53/api/job?apikey={apikey}",json=payload, headers=headers)
    if res.status_code is 204:
        messages.info(request,'Printing Started!!!')
    elif res.status_code == 409:
        messages.info(request,"Conflict!")
    return redirect('Home')

def pause(request):
    payload = { 'command': 'pause', 'action': 'pause'}
    headers = {'content-type': 'application/json'}
    
    res = requests.post(f"http://192.168.1.53/api/job?apikey={apikey}",json=payload, headers=headers)
    if res.status_code == 409:
        messages.info(request,"Conflict!")
    return redirect('Home')

def resume(request):
    payload = { 'command': 'pause', 'action': 'resume'}
    headers = {'content-type': 'application/json'}
    
    res = requests.post(f"http://192.168.1.53/api/job?apikey={apikey}",json=payload, headers=headers)
    if res.status_code == 409:
        messages.info(request,"Conflict!")
    return redirect('Home')

def cancel(request):
    payload = { 'command': 'cancel'}
    headers = {'content-type': 'application/json'}
    
    res = requests.post(f"http://192.168.1.53/api/job?apikey={apikey}",json=payload, headers=headers)
    if res.status_code == 409:
        messages.info(request,"Conflict!")
    return redirect('Home')


def upload(request):
    if request.method == 'POST' and request.FILES['gfile']:
        print("Posted file: {}".format(request.FILES['gfile']))
        myfile = request.FILES['gfile']
        #files = {'file': myfile.read()}
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        
        #files = {'file': myfile.read()}
        #payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"file\"; \
                #  filename=\""+myfile.name+"\"\r\nContent-Type: application/octet-stream\n\r \
                #  \r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
        f = open( "."+MEDIA_URL+filename, 'rb')
        file1 = (filename, f)    
        #print(MEDIA_URL+filename)
        #headers = {'content-type': "multipart/form-data"}
        #headers = {'X-Api-Key' : 'EB9B26499B6E49609D1EF1C1A6680985'}
    
        client.upload(file1)   
    return HttpResponse('File uploaded successfully...')
    

def logout(request):
    global apikey
    url1 = f"http://192.168.1.53/api/logout?apikey={apikey}"
    response = requests.post(url1)
    if response.status_code is 204:
        auth.logout(request)
        print("Logged out")
        return redirect('login')
    else:
        print('error')
        messages.error(request, 'Error while logging out!!!')
        return redirect('Home')
