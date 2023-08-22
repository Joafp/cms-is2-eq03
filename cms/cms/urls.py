
from django.contrib import admin
from django.urls import path,include
urlpatterns = [
    #Añado los urls de login
    path('',include('login.urls')),
    path('admin/', admin.site.urls),
    path('accounts/',include('django.contrib.auth.urls')),
]
