
from django.urls import path,include 
from . import views
from django.contrib.auth import urls
from core import views as coreviews
urlpatterns = [
   path('',views.vista_login,name='login'),  
   path('menuprincipal/',coreviews.vista_MenuPrincipal,name='MenuPrincipal'),
   path('registrarse/',coreviews.vista_registrarse,name='registro'),
] 
 