from django.shortcuts import redirect
import math
from django.http import HttpResponse
import json

def jsonp(request, content):
    if request.GET.get('callback'):
        callback = request.GET.get('callback').strip()
        return HttpResponse(callback + '(' + json.dumps(content, ensure_ascii=False, indent=4) + ')', content_type="application/json; charset=utf-8")
    else:
        return HttpResponse(json.dumps(content, ensure_ascii=False, indent=4), content_type="application/json; charset=utf-8")

def checkmodule(module):
    import imp
    try:
        imp.find_module(module)
        return True
    except ImportError:
        return False

def redirectlogin(request):
    if request.META['QUERY_STRING']:
        return redirect('/u/login/?next=' + request.path + '?' + request.META['QUERY_STRING'])
    else:
        return redirect('/u/login/?next=' + request.path)

def deg2rad(deg):
    return deg * (math.pi / 180)

def geotod(lat1, lon1, lat2, lon2):
    R = 6378.137
    dLat = deg2rad(lat2-lat1)
    dLon = deg2rad(lon2-lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return int(d * 1000)

def deltatime2second(deltatime):
    if hasattr(deltatime, "total_seconds"):
        return deltatime.total_seconds()
    else: 
        return (deltatime.microseconds + (deltatime.seconds +  deltatime.days * 24 * 3600) * 10**6) / 10**6
