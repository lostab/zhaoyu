# -*- coding: utf-8 -*-
import sys
import importlib
importlib.reload(sys)
# Create your views here.

from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import redirect, render
import datetime
from django.utils.timezone import utc
import json
from app.item.models import *
from app.item.forms import *
from app.tag.models import *
from django.forms.utils import ErrorList
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app.user.models import *
from cfg import *
from app.main.__init__ import *
from app.item.__init__ import *
from django.forms.models import inlineformset_factory
from django.db.models import Q

def Index(request):
    try:
        #tags = Tag.objects.all().order_by('?')[:1000]
        tags = Tag.objects.all().order_by('?')
    except Tag.DoesNotExist:
        tags = None

    content = {
        'tags': tags
    }

    return render(request, 'tag/index.html', content)

def View(request, id):
    try:
        tag = Tag.objects.get(id=id)
    except:
        tag = None
    try:
        items = Item.objects.select_related('user').filter(useritemrelationship__isnull=True).filter(Q(belong__isnull=True)).filter(Q(status__isnull=True) | Q(status__exact='')).filter(Q(tag__id=id)).all().prefetch_related('itemcontent_set', 'itemcontent_set__contentattachment_set', 'tag')

        items = sort_items(items, request.GET.get('page'))

        currentpage = items.number

        itemlist = []
        for item in items:
            itemlist.append(item)

        items = itemlist
        items = sorted(items, key=lambda item:item.lastsubitem.create, reverse=True)
    except Item.DoesNotExist:
        items = None

    try:
        tags = Tag.objects.all().order_by('?')[:10]
    except Tag.DoesNotExist:
        tags = None

    content = {
        'items': items,
        'tag': tag,
        'tags': tags
    }
    if request.GET.get('type') == 'json':
        content = {
            'page': currentpage,
            'items': []
        }

        return jsonp(request, content)
    return render(request, 'tag/view.html', content)

def Update(request, id):
    return redirect('/')
