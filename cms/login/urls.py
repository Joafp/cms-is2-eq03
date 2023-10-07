from django.urls import path,include
from . import views
from core import views as menu
from login import views as cat
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
   path('',views.vista_login,name='login'),  
   path('registro/', views.registro, name='registro'),
   path('logout/',views.cerrar_sesion,name='CerrarSesion'),
   path('accounts/',include('django.contrib.auth.urls')),
   path('administrador/',views.vista_admin,name='Administrador'),
   path('buscar/', views.buscar_contenido, name='buscar_contenido')
] 

