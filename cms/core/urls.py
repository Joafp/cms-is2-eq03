from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.vista_MenuPrincipal,name='MenuPrincipal'),
    path('main_trabajador/',views.vista_trabajador,name='maintrabajador'),
    path('login/',include('login.urls')),
    path('categoria/<str:nombre>/', views.categoria,name='cat'),
    path('crear/',views.crear_categoria,name='Categoria'),
    path('desactivar/',views.desactivar_categoria,name='desc'),
    path('roles/',views.vista_roles, name='gestion'),
    path('asignar/',views.asignar_rol,name='asignacion'),
    path('desasignar/',views.remover_rol,name='desasignar')
]
