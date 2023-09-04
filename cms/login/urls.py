from django.urls import path,include
from . import views
from core import views as menu
from categoria import views as cat
urlpatterns = [
   path('',views.vista_login,name='login'),  
   path('menuprincipal/',menu.vista_MenuPrincipal,name='MenuPrincipal'),
   path('registro/', views.registro, name='registro'),
   path('main_trabajador/',menu.vista_trabajador,name='maintrabajador'),
   path('logout/',views.cerrar_sesion,name='CerrarSesion'),
   path('accounts/',include('django.contrib.auth.urls')),
   path('categorias/',include('categoria.urls')),
   path('administrador/',views.vista_admin,name='Administrador'),
] 

 