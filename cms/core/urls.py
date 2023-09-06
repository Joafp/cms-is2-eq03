from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import CrearContenido,VistaArticulos,VistaContenidos
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.conf import settings
urlpatterns = [
    path('',views.vista_MenuPrincipal,name='MenuPrincipal'),
    path('main_trabajador/',views.vista_trabajador,name='maintrabajador'),
    path('login/',include('login.urls')),
    path('crearcontenido/',login_required(CrearContenido.as_view(),login_url="/login"),name='crear_contenido'),
    path('articulo/<int:pk>', login_required(VistaArticulos.as_view(),login_url="/login"),name='detalles_articulo'),
    path('contenidos',VistaContenidos.as_view(),name='vistacontenidos'),
    path('categoria/<str:nombre>/', views.categoria,name='cat'),
    path('crear/',views.crear_categoria,name='Categoria'),
    path('desactivar/',views.desactivar_categoria,name='desc'),
    path('roles/',views.vista_roles, name='gestion'),
    path('asignar/',views.asignar_rol,name='asignacion'),
    path('desasignar/',views.remover_rol,name='desasignar'),
]
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
