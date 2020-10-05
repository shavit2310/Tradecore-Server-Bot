#!/bin/python3

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db.models import Q

from . import models


def index(request):
    return HttpResponse('Hello, You''re at the social network of Trade_core Server.  '
                        'You can go to Admin, by adding: /admin to url, or run BOT with specific action to perform in '
                        'App core')
# Create new user
@csrf_exempt
def sign_up(request):
    jwt_code = models.User.create(request.body)
    return HttpResponse(jwt_code)


# Login specific user
@csrf_exempt
def login(request):
    succ_fail_flag = models._login(request.body)

    return HttpResponse(succ_fail_flag)


# After login create some posts
@csrf_exempt
def create_post(request):

    user = models._retreive_user(request.body)
    # influence from segment issue error to resolve
    if isinstance(user,models.User):
        response= models.Post.create(user)
    else:
        response = user

    return HttpResponse(response)


# After login create do likes
@csrf_exempt
def do_like(request):
    op_like = (request.body).decode('utf-8').split('=')
    # bring user  & post objects

    user = models._retreive_user(op_like[0])
    if isinstance(user, models.User):
        post = models._is_post(int(op_like[1]))
        if isinstance(post, models.Post):
            succ_fail_flag= models.Like.create(user,post)
        else:
            succ_fail_flag = post
    else:
        succ_fail_flag = user

    return HttpResponse(succ_fail_flag)

# After login create do unlike
@csrf_exempt
def do_unlike(request):
    op_unlike = (request.body).decode('utf-8').split('=')
    # bring user  & post objects

    user = models._retreive_user(op_unlike[0])
    if isinstance(user, models.User):
            post = models._is_post(int(op_unlike[1]))
            if isinstance(post, models.Post):
                #like = models.Like.retreive_like(user, post)
                #like = models.Like.objects.value_list(user_related_like=user, post_related_like =post)
                #like = models._is_like(user,post)
                op_like = models.Like.objects.filter(user_related_like=user)
                for i in op_like:
                    like= op_like.objects.get(post_related_like = post)
                    print(f'{like}Y')
                if isinstance(op_like, models.Like):
                    del op_like
                else:
                    succ_fail_flag = op_like
            else:
                succ_fail_flag = post
    else:
        succ_fail_flag = user

    return HttpResponse(succ_fail_flag)




