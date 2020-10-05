#!/bin/python3
# ! Django 3.1.1

from django.urls import path
from . import views

urlpatterns = [
    # In /Server
    path('', views.index, name='index'),
    # sign_up users
    path('sign_up', views.sign_up, name='sign_up'),
    # login to specific user
    path('login', views.login, name='login'),
    # create post for specific user
    path('create_post', views.create_post, name='create_post'),
    # do like for specific user
    path('do_like', views.do_like, name='do_like'),
    # do 1 like for specific user
    path('do_unlike', views.do_unlike, name='do_unlike'),

]
