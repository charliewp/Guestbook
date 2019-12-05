from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

#from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'signin/', views.sign_in, name='sign_in'),
    url(r'login/', views.login, name='login'),
    url(r'logout/', views.logout, name='logout'),
    url(r'services*', views.services, name='services'),
    url(r'select/', views.select, name='select'),
    url(r'staff/', views.staff, name='staff'),
    url(r'staffqueue*', views.staffqueue, name='staffqueue'),
    url(r'note*', views.note, name='note'),
    url(r'prompt*', views.prompt, name='prompt'),
    url(r'reporter*', views.reporter, name='reporter'),
    url(r'queue*', views.queue, name='queue'),
    url(r'createalias/', views.createalias, name='createalias'),
    url(r'resetalias/', views.resetalias, name='resetalias'),
    url(r'thankyou*', views.thankyou, name='thankyou'),
    url(r'picture*', views.picture, name='picture'),
    url(r'postimage*', views.postimage, name='postimage'),
    url(r'whoishere*', views.whoishere, name='whoishere')
]