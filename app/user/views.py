# -*- coding: utf-8 -*-
import sys
import importlib
importlib.reload(sys)
# Create your views here.

from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import redirect, render
from datetime import datetime, timedelta
from django.utils import timezone
import json
import time
from django.contrib.auth.models import User
from django.contrib.auth import *
from django.contrib.auth.forms import *
from django.core.mail import send_mail
from cfg import *
from app.main.__init__ import *
from app.user.models import *
from app.user.forms import *
from app.item.models import *
from app.item.forms import *
from django.db.models import Q
from django.forms.utils import ErrorList
from django.views.decorators import csrf
import os
from django.utils.html import escape
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def Main(request):
    user = request.user
    if user.is_authenticated:
        content = {}
        if request.GET.get('type') == 'json':
            content = {
                'status': 'success',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'name': user.userprofile.info,
                    'avatar': (user.userprofile.openid and '//' in str(user.userprofile.avatar)) and str(user.userprofile.avatar) or ((user.userprofile.avatar) and '/s/' + str(user.userprofile.avatar) or '/s/avatar/n.png'),
                    'page': user.userprofile.page,
                    'create': str(user.userprofile.create)
                }
            }
            return jsonp(request, content)
        return render(request, 'user/index.html', content)
    else:
        if request.GET.get('type') == 'json':
            content = {
                'status': 'error'
            }
            return jsonp(request, content)
        return redirectlogin(request)

def Signup(request):
    next = None
    if request.GET.get('next'):
        next = request.META['QUERY_STRING'].split('next=')[1]
        if request.GET.get('next'):
            if request.GET.get('next')[0] != '/':
                return redirect('/u/signup/')
            else:
                nextpath = request.GET.get('next').split('?')[0]
                if nextpath[0] != '/' or nextpath in ['', '/', '/u/login/', '/u/signup/']:
                    return redirect('/u/signup/')
    if request.user.is_authenticated:
        if request.GET.get('type') == 'json':
            content = {
                'status': 'success'
            }
            return jsonp(request, content)
        if next:
            return redirect(next)
        else:
            return redirect('/')
    if request.method == 'GET':
        if request.GET.get('type') == 'json':
            content = {
                'csrf_token': unicode(csrf(request)['csrf_token'])
            }
            return jsonp(request, content)
        return render(request, 'user/signup.html', {})
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            newuser = form.save(commit=False)
            newuser.last_login = timezone.now()
            newuser.save()

            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1'] = form.cleaned_data['password2']
            user = User.objects.get(username=username)
            userprofile = UserProfile(user=user)
            userprofile.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            if request.GET.get('type') == 'json':
                content = {
                    'status': 'success'
                }
                return jsonp(request, content)
            if next:
                return redirect('/u/settings/?prev=signup&next=' + next)
            else:
                return redirect('/u/settings/?prev=signup')
        else:
            if request.GET.get('type') == 'json':
                content = {
                    'status': 'error',
                    'csrf_token': unicode(csrf(request)['csrf_token']),
                    'errors': [(k, map(unicode, v)) for k, v in form.errors.items()]
                }
                return jsonp(request, content)
            return render(request, 'user/signup.html', { 'form': form })

def Login(request):
    next = None

    if request.GET.get('next'):
        if request.GET.get('next')[0] != '/':
            return redirect('/u/login/')
        else:
            nextpath = request.GET.get('next').split('?')[0]
            if nextpath[0] != '/' or nextpath in ['', '/', '/a/', '/u/login/', '/u/signup/']:
                return redirect('/u/login/')
    if request.user.is_authenticated:
        if request.GET.get('type') == 'json':
            content = {
                'status': 'success'
            }
            return jsonp(request, content)
        if next:
            return redirect(next)
        else:
            return redirect('/')
    if request.method == 'GET':
        if request.GET.get('type') == 'json':
            content = {
                'csrf_token': unicode(csrf(request)['csrf_token'])
            }
            return jsonp(request, content)
        return render(request, 'registration/login.html', { 'next': next })
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if request.GET.get('type') == 'json':
                        content = {
                            'status': 'success'
                        }
                        return jsonp(request, content)
                    if next:
                        return redirect(next)
                    else:
                        return redirect('/')
                else:
                    if request.GET.get('type') == 'json':
                        content = {
                            'status': 'error',
                            'csrf_token': unicode(csrf(request)['csrf_token']),
                            'errors': [(k, map(unicode, v)) for k, v in form.errors.items()]
                        }
                        return jsonp(request, content)
                    return render(request, 'registration/login.html', { 'form': form, 'next': next })
            else:
                if request.GET.get('type') == 'json':
                    content = {
                        'status': 'error',
                        'csrf_token': unicode(csrf(request)['csrf_token']),
                        'errors': [(k, map(unicode, v)) for k, v in form.errors.items()]
                    }
                    return jsonp(request, content)
                return render(request, 'registration/login.html', { 'form': form, 'next': next })
        else:
            if request.GET.get('type') == 'json':
                content = {
                    'status': 'error',
                    'csrf_token': unicode(csrf(request)['csrf_token']),
                    'errors': [(k, map(unicode, v)) for k, v in form.errors.items()]
                }
                return jsonp(request, content)
            return render(request, 'registration/login.html', { 'form': form, 'next': next })

def Logout(request):
    next = None
    if request.GET.get('next'):
        next = request.META['QUERY_STRING'].split('next=')[1]
        if request.GET.get('next')[0] != '/':
            return redirect('/u/login/')
        else:
            nextpath = request.GET.get('next').split('?')[0]
            if nextpath[0] != '/' or nextpath in ['', '/', '/u/login/', '/u/signup/']:
                return redirect('/u/login/')
    logout(request)
    if request.GET.get('type') == 'json':
        content = {
            'status': 'success'
        }
        return jsonp(request, content)
    if next:
        return redirect(next)
    else:
        return redirect('/')

def Settings(request):
    prev = None
    if request.GET.get('prev'):
        prev = request.GET.get('prev')
    next = None
    if request.GET.get('next'):
        next = request.META['QUERY_STRING'].split('next=')[1]
        nextpath = request.GET.get('next').split('?')[0]
        if prev and next and (nextpath[0] != '/' or nextpath in['', '/u/login/', '/u/signup/']):
            return redirect('/u/settings/?prev=' + prev)
    if request.user.is_authenticated:
        if request.method == 'GET':
            if request.GET.get('type') == 'json':
                content = {
                    'csrf_token': unicode(csrf(request)['csrf_token']),
                    'prev': prev,
                    'next': next
                }
                return jsonp(request, content)
            content = {
                'prev': prev,
                'next': next
            }
            return render(request, 'user/settings.html', content)
        if request.method == 'POST':
            userprofile = UserProfile.objects.get(user=request.user)
            form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
            if form.is_valid():
                userprofile = form.save()
                if userprofile.avatar and checkmodule('PIL'):
                    from PIL import Image
                    avatar_file = os.path.join(settings.MEDIA_ROOT, 'avatar', str(request.user.username) + '.png')
                    if os.path.isfile(avatar_file):
                        avatar = Image.open(avatar_file)
                        max_size = 64
                        if avatar.size[0] > avatar.size[1]:
                            size = (max_size, int(max_size * avatar.size[1] / avatar.size[0]))
                        else:
                            size = (int(max_size * avatar.size[0] / avatar.size[1]), max_size)
                        avatar.thumbnail(size, Image.ANTIALIAS)

                        def resize_avatar(avatar, p):
                            avatar_size = os.path.getsize(avatar_file)
                            if avatar_size > 5 * 1024 and avatar.size[0] > 1 and avatar.size[1] > 1:
                                p = p * 0.75
                                avatar.thumbnail([int(p * s) for s in avatar.size], Image.ANTIALIAS)
                                avatar = avatar.resize(size)
                                avatar.save(avatar_file, optimize=True)
                                if os.path.getsize(avatar_file) >= avatar_size:
                                    resize_avatar(avatar, p)
                        resize_avatar(avatar, 1)

                if request.GET.get('type') == 'json':
                    content = {
                        'status': 'success'
                    }
                    return jsonp(request, content)
                if next:
                    return redirect(next)
                else:
                    return redirect(Main)
            else:
                if request.GET.get('type') == 'json':
                    content = {
                        'status': 'error',
                        'csrf_token': unicode(csrf(request)['csrf_token']),
                        'errors': [(k, map(unicode, v)) for k, v in form.errors.items()]
                    }
                    return jsonp(request, content)
                content = {
                    'prev': prev,
                    'next': next,
                    'form': form
                }
                return render(request, 'user/settings.html', content)
    else:
        if request.GET.get('type') == 'json':
            content = {
                'status': 'error'
            }
            return jsonp(request, content)
        return redirectlogin(request)

def UserPage(request, username):
    try:
        user = User.objects.get(username=username)
        try:
            userprofile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user = None
    except User.DoesNotExist:
        user = None

    items, belongitems = get_item_by_user(user, request)

    if request.GET.get('type') == 'json':
        if user:
            content = {
                'status': 'success',
                'user': {
                    'username': user.username,
                    'info': user.userprofile.info,
                    'avatar': (user.userprofile.openid and '//' in str(user.userprofile.avatar)) and str(user.userprofile.avatar) or ((user.userprofile.avatar) and '/s/' + str(user.userprofile.avatar) or '/s/avatar/n.png'),
                    'profile': user.userprofile.profile,
                    'page': user.userprofile.page
                }
            }
        else:
            content = {
                'status': 'error'
            }
        return jsonp(request, content)
    content = {
        'viewuser': user,
        'items': items,
        'belongitems': belongitems
    }
    return render(request, 'user/defaultpage.html', content)

def Page(request, username):
    try:
        user = User.objects.get(username=username)
        try:
            userprofile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user = None
    except User.DoesNotExist:
        user = None
    if request.GET.get('type') == 'json':
        if user:
            content = {
                'status': 'success',
                'user': {
                    'username': user.username,
                    'info': user.userprofile.info,
                    'avatar': (user.userprofile.openid and '//' in str(user.userprofile.avatar)) and str(user.userprofile.avatar) or ((user.userprofile.avatar) and '/s/' + str(user.userprofile.avatar) or '/s/avatar/n.png'),
                    'profile': user.userprofile.profile,
                    'page': user.userprofile.page
                }
            }
        else:
            content = {
                'status': 'error'
            }
        return jsonp(request, content)
    content = {
        'user': user
    }
    if user and user.userprofile.page:
        return render(request, 'user/page.html', content)
    else:
        return render(request, 'user/defaultpage.html', content)

def Notify(request):
    user = request.user
    if user.is_authenticated:
        try:
            notify = UserNotify.objects.all().filter(user=request.user).order_by('-created')
            for i in notify:
                if i.item.get_root_items():
                    i.rootitem = i.item.get_root_items()[0]
                else:
                    i.rootitem = None
        except User.DoesNotExist:
            notify = None

        content = {
            'notify': notify
        }
        if request.GET.get('type') == 'json':
            messages = []
            for i in notify:
                message = {
                    'rootitem': {
                        'id': str(i.rootitem.id)
                    },
                    'parent': {
                        'id': str(i.item.belong.all().first().id),
                        'content': escape(str(i.item.belong.all().first().itemcontent_set.all().first().content.strip().splitlines()[0]))
                    },
                    'item': {
                        'id': str(i.item.id),
                        'content': escape(str(i.item.itemcontent_set.all().first().content.strip().splitlines()[0]).encode('utf-8')),
                        'user': {
                            'username': i.item.user.username,
                            'info': escape(i.item.user.userprofile.info),
                            'avatar': (i.item.user.userprofile.openid and '//' in str(i.item.user.userprofile.avatar)) and str(i.item.user.userprofile.avatar) or ((i.item.user.userprofile.avatar) and '/s/' + str(i.item.user.userprofile.avatar) or '/s/avatar/n.png'),
                            'profile': escape(i.item.user.userprofile.profile),
                            'page': escape(i.item.user.userprofile.page)
                        }
                    },
                    'created': str(i.created + timedelta(hours=8)),
                }
                messages.append(message)
            content = {
                'status': 'success',
                'notify': {
                    'count': len(notify),
                    'messages': messages
                }
            }
            return jsonp(request, content)
        return render(request, 'user/notify.html', content)
    else:
        if request.GET.get('type') == 'json':
            content = {
                'status': 'error'
            }
            return jsonp(request, content)
        return redirectlogin(request)

def Feedback(request):
    if request.method == 'GET':
        return render(request, 'user/feedback.html', {})
    if request.method == 'POST':
        if request.POST.get('feedback'):
            feedback = request.POST['feedback']
            try:
                feedbackuser = ''
                if request.user.username:
                    feedbackuser = str(request.user.username) + ': '
                send_mail('Hulu', feedbackuser + feedback, os.environ['system_mail_username'], [os.environ['receive_mail']], fail_silently=False)
                return render(request, 'user/feedback.html', { 'submit': 'true' })
            except:
                return redirect('/u/feedback/')
        else:
            return redirect('/u/feedback/')

def List(request):
    try:
        users = User.objects.all().order_by('-date_joined')
    except User.DoesNotExist:
        users = None

    paginator = Paginator(users, 100)
    itemlist = []
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    content = {
        'users': users
    }
    return render(request, 'user/list.html', content)

def Avatar(request, avatar):
    def get_avatar_object():
        avatar_object = None
        avatar_file = os.path.join(settings.MEDIA_ROOT, 'avatar', avatar)
        if not os.path.isfile(avatar_file):
            avatar_file = os.path.join(settings.MEDIA_ROOT, 'avatar', 'n.png')
        avatar_object = open(avatar_file, 'rb').read()

        if avatar_object:
            return avatar_object
        else:
            return get_avatar_object()

    return HttpResponse(get_avatar_object(), content_type='image/png')
