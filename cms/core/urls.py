from django.urls import path,include
from . import views

urlpatterns = [
    path('menuprincipal/',views.vista_MenuPrincipal,name='MenuPrincipal'),
    path('',include('login.urls'))
]
