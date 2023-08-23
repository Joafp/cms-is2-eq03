from django.urls import path
from . import views

urlpatterns = [
    path('menuprincipal/',views.vista_MenuPrincipal,name='MenuPrincipal'),
    path('main_trabajador/',views.vista_trabajador,name='maintrabajador')
]
