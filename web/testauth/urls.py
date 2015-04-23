from django.conf.urls import include, url
from django.contrib import admin
from testauth import views 

urlpatterns = [
   url(r'^login/', views.loginview),
   url(r'^auth/', views.auth_and_login),
   url(r'^signup/', views.sign_up_in),
   #url(r'^logout/', views.logout),
   url(r'^logout/$', 'django.contrib.auth.views.logout',
                          {'next_page': '/login/'}),
   url(r'^$', views.secured),
]
