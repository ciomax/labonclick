"""labonclick URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from resource_manager import views
from django.http import HttpResponseRedirect
from rest_framework import routers

app_name = 'resource_manager'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda x: HttpResponseRedirect('/home/')),
    path('', include('resource_manager.urls', namespace="resource_manager")),
    path('logout', views.user_logout, name='logout'),
    path('celery-progress/', include('celery_progress.urls')),
    # path('lab/', include('resource_manager.urls', namespace="resource_manager")),
]
