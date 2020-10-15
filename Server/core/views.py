#!/bin/python3

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from . import models


def index(request):
    '''Uploading the app'''
    return HttpResponse('Hello, You are at the social network of Trade_core Server.  '
                        'You can go to Admin, by adding: /admin to url, or run BOT with specific action to perform in '
                        'App trade')


@csrf_exempt
def sign_up(request):
    '''Create new user'''
    jwt_code = models.User.create(request.body)
    return HttpResponse(jwt_code)


@csrf_exempt
def login(request):
    '''Login specific user'''
    response = False

    op_mail, op_id = models._decode(request.body)
    if not op_id == -1:
        user_obj = models.User.objects.get(pk=op_id)

        if user_obj.pk != None and user_obj.email == op_mail:
            response = user_obj.pk

    return HttpResponse(response)


@csrf_exempt
def create_post(request):
    '''Create post'''
    response = False

    user_obj = models.User.objects.get(pk=int(request.body.decode('utf-8')))
    if user_obj:
        response = models.Post.create(user_obj)

    return HttpResponse(response)


@csrf_exempt
def do_like(request):
    ''' Do like'''
    res = False

    op_like = request.body.decode('utf-8').split('=')
    like = models.Post.users.through.objects.get(user_related=op_like[0], post_related=op_like[1])

    if isinstance(like, models.Like):
        res = like.do_like()

    return HttpResponse(res)


@csrf_exempt
def do_unlike(request):
    ''' Do unlike'''
    '''Create Like - do like'''
    res = False

    op_unlike = request.body.decode('utf-8').split('=')
    unlike = models.Post.users.through.objects.get(user_related=op_unlike[0], post_related=op_unlike[1])

    if isinstance(unlike, models.Like):
        res = unlike.do_unlike()

    return HttpResponse(res)

