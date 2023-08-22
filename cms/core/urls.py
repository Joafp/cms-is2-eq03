from django.urls import path
from . import views

urlpatterns = [
    path('menuprincipal/',views.vista_MenuPrincipal,name='MenuPrincipal')
]
