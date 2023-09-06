from django.urls import path,include
from . import views
from core import views as menu
from login import views as cat
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
   path('',views.vista_login,name='login'),  
   path('registro/', views.registro, name='registro'),
   path('main_trabajador/',menu.vista_trabajador,name='maintrabajador'),
   path('logout/',views.cerrar_sesion,name='CerrarSesion'),
   path('accounts/',include('django.contrib.auth.urls')),
   path('administrador/',views.vista_admin,name='Administrador'),
]  

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)