from django.urls import path,include
from . import views
from .views import CrearContenido,VistaArticulos,VistaContenidos
urlpatterns = [
    path('',views.vista_MenuPrincipal,name='MenuPrincipal'),
    path('main_trabajador/',views.vista_trabajador,name='maintrabajador'),
    path('login/',include('login.urls')),
    path('crearcontenido/',CrearContenido.as_view(),name='crear_contenido'),
    path('articulo/<int:pk>', VistaArticulos.as_view(),name='detalles_articulo'),
    path('contenidos',VistaContenidos.as_view(),name='vistacontenidos'),
    path('categoria/<str:nombre>/', views.categoria,name='cat'),
    path('crear/',views.crear_categoria,name='Categoria'),
    path('desactivar/',views.desactivar_categoria,name='desc'),
    path('roles/',views.vista_roles, name='gestion'),
    path('asignar/',views.asignar_rol,name='asignacion'),
    path('desasignar/',views.remover_rol,name='desasignar')
]
