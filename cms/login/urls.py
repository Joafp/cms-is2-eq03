from django.urls import path
from . import views
from core import views as menu

urlpatterns = [
   path('',views.vista_login,name='login'),  
   path('registro/',views.registro,name='registro'),
   path('menuprincipal/',menu.vista_MenuPrincipal,name='MenuPrincipal'),
] 
 