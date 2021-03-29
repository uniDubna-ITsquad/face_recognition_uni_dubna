from django.shortcuts import render
from django.http import HttpResponse
from main_server.models import Cameras

def index(request):
    res = ''
    for cam in Cameras.objects.all():
        res += f"""\
<p><a href='{cam.ip}'>{cam.ip}</a></p>
"""
    print(res)
    return HttpResponse(res)

def cam(request, cam_ip):
    return HttpResponse(f'<p>{cam_ip}</p>')