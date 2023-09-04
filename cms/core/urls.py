from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.vista_MenuPrincipal,name='MenuPrincipal'),
    path('main_trabajador/',views.vista_trabajador,name='maintrabajador'),
    path('login/',include('login.urls')),
    path('categorias/',include('categoria.urls')),
    path('categoria/<str:nombre>/', views.categoria,name='cat')
]
