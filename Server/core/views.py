#!/bin/python3

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from . import models


def index(request):
    '''For uploading the app'''
    return HttpResponse('Hello, You''re at the social network of Trade_core Server.  '
                        'You can go to Admin, by adding: /admin to url, or run BOT with specific action to perform in '
                        'App core')


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
            response = user_obj

    return HttpResponse(response)


@csrf_exempt
def create_post(request):
    '''Create post'''

    user = models.User.objects.get(pk=(request.body).decode('utf-8'))

    # influence from segment issue error to resolve
    if isinstance(user, models.User):
        response = models.Post.create(user)
    else:
        response = user

    return HttpResponse(response)


@csrf_exempt
def do_like(request):
    '''Create Like - do like'''
    res = False

    op_like = (request.body).decode('utf-8').split('=')
    # bring user  & post objects
    user = models.User.objects.get(pk=op_like[0])
    post = models.Post.objects.get(pk=op_like[1])

    if isinstance(user, models.User) and isinstance(post, models.Post):
        res = models.Like.create(user,post)

    return HttpResponse(res)


@csrf_exempt
def do_unlike(request):
    '''Delete Like - do unlike'''
    res = False

    op_unlike = (request.body).decode('utf-8').split('=')
    # bring user  & post objects
    user = models.User.objects.get(pk=op_unlike[0])
    post = models.Post.objects.get(pk=op_unlike[1])

    if isinstance(user, models.User) and isinstance(post, models.Post):
        unlike = models.Like.objects.filter(user_related_like=user, post_related_like=post)
        if isinstance(unlike[0], models.Like):
            res = unlike[0].do_unlike()

    return HttpResponse(res)
