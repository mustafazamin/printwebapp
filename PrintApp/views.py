import json

import requests
from django.contrib import messages
from django.contrib.auth.models import auth
from django.http import HttpResponse
from django.shortcuts import redirect, render
from urllib3.connectionpool import HTTPConnectionPool

global apikey
apikey=''

def login(request):

    if request.user.is_authenticated:
        return redirect('Home')

    else:
        if request.method=='POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = auth.authenticate(username=username, password=password)
            
            if user is not None:
                try:
                    url = "http://192.168.1.53/api/login?user="+username+"&pass="+password
                    response = requests.post(url)
                    result = response.json()
                    global apikey
                    apikey = result.get('apikey')
                    print(apikey)
                    if apikey != '':
                        auth.login(request, user)
                        return redirect('Home')
                except:
                    messages.info(request, 'Connection timeout... Try again!')
            else:
                messages.error(request,'Invalid Credentials... Try again!')
                return redirect('login')

    return render(request, 'index.html')


def Home(request):
    global apikey
    print(apikey)
    return render(request, 'Home.html')


def connect(request):
    payload = { 'command': 'connect'}
    headers = {'content-type': 'application/json'}
    global apikey
    res = requests.post(f"http://192.168.1.53/api/connection?apikey={apikey}",json=payload, headers=headers)
    if res.status_code is 204:
        messages.info(request,'Connection Successful!!!')
    return render(request, 'Home.html')

def disconnect(request):
    payload = { 'command': 'disconnect'}
    headers = {'content-type': 'application/json'}
    global apikey
    res = requests.post(f"http://192.168.1.53/api/connection?apikey={apikey}",json=payload, headers=headers)
    if res.status_code is 204:
        messages.info(request,'Disconnected!!!')
    return render(request, 'Home.html')


def select(request):
    payload = { 'command': 'select'}
    headers = {'content-type': 'application/json'}
    global apikey
    res = requests.post(f"http://192.168.1.53/api/files/local/aaliyah_f1.gcode?apikey={apikey}",json=payload, headers=headers)
    if res.status_code is 204:
        messages.info(request,'File selected!!!')
    return render(request, 'Home.html')

def start(request):
    payload = { 'command': 'start'}
    headers = {'content-type': 'application/json'}
    global apikey
    res = requests.post(f"http://192.168.1.53/api/job?apikey={apikey}",json=payload, headers=headers)
    if res.status_code is 204:
        messages.info(request,'Printing Started!!!')
    elif res.status_code == 409:
        messages.info(request,"Conflict!")
    return render(request, 'Home.html')

def pause(request):
    payload = { 'command': 'pause', 'action': 'pause'}
    headers = {'content-type': 'application/json'}
    global apikey
    res = requests.post(f"http://192.168.1.53/api/job?apikey={apikey}",json=payload, headers=headers)
    if res.status_code is 204:
        messages.info(request,'Paused!')
    elif res.status_code == 409:
        messages.info(request,"Conflict!")
    return render(request, 'Home.html')

def resume(request):
    payload = { 'command': 'pause', 'action': 'resume'}
    headers = {'content-type': 'application/json'}
    global apikey
    res = requests.post(f"http://192.168.1.53/api/job?apikey={apikey}",json=payload, headers=headers)
    if res.status_code is 204:
        messages.info(request,'Resumed!')
    elif res.status_code == 409:
        messages.info(request,"Conflict!")
    return render(request, 'Home.html')

def cancel(request):
    payload = { 'command': 'cancel'}
    headers = {'content-type': 'application/json'}
    global apikey
    res = requests.post(f"http://192.168.1.53/api/job?apikey={apikey}",json=payload, headers=headers)
    if res.status_code is 204:
        messages.info(request,'Cancelled!!!')
    elif res.status_code == 409:
        messages.info(request,"Conflict!")
    return render(request, 'Home.html')


def upload(request):
    if request.method == 'POST':
        file = request.FILES['gfile']
        #with open(file,'rb') as filedata:
            #fdata = {'file':filedata}
        
        headers = {'content-type': 'multipart/form-data'}
        global apikey
        url = f"http://192.168.1.53/api/files/local?apikey={apikey}"
        response = requests.post(url,files=file,headers=headers)
        if response.status_code == 201:
            messages.info(request, 'File uploaded!!!')
        elif response.status_code == 400:
            messages.info(request, 'Bad request!')
        elif response.status_code == 404:
            messages.info(request, 'Not found location!')
        elif response.status_code == 409:
            messages.info(request, 'Conflict!')
        elif response.status_code == 415:
            messages.info(request, 'Unsupported media file')
    return render(request, 'Home.html')    
    

def logout(request):
    global apikey
    url = f"http://192.168.1.53/api/logout?apikey={apikey}"
    response = requests.post(url)
    if response.status_code is 204:
        auth.logout(request)
        print("Logged out")
        return redirect('login')
    else:
        print("Error")
        messages.info(request, 'Error logging out!!!')
        return redirect('Home')


    return render(request, 'index.html')
