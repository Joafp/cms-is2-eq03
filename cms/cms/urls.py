
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import urls

urlpatterns = [
    path('', include('core.urls')),
    #path('', include('login.urls')),
    #path('accounts/', include('django.contrib.auth.urls')),
]