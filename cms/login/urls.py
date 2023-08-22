
from django.urls import path,include 
from . import views
from django.contrib.auth import urls
urlpatterns = [
   path('',views.vista_login,name='login'),  
<<<<<<< HEAD
   path('registro/',views.registro,name='registro'),
=======
   path('menuprincipal/',menu.vista_MenuPrincipal,name='MenuPrincipal'),
>>>>>>> origin/hito1_carlosayala
] 
 