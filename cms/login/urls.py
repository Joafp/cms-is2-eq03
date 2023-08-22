
from django.urls import path,include 
from . import views
from django.contrib.auth import urls
urlpatterns = [
   path('',views.vista_login,name='login'),  
   path('registro/',views.registro,name='registro'),
] 
 