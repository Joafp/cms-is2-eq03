from django.urls import path,include
from . import views
from .views import CrearContenido,VistaArticulos,VistaContenidos,VistaArticulosEditor,VistaArticulosRevision
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.conf import settings
urlpatterns = [
    path('',views.vista_MenuPrincipal,name='MenuPrincipal'),
    path('main_trabajador/',views.vista_trabajador,name='maintrabajador'),
    path('login/',include('login.urls')),
    path('crearcontenido/',CrearContenido.as_view(),name='crear_contenido'),
    path('editarcontenido/',views.vista_editor,name='Editar'),
    path('publicarcontenido/',views.vista_publicador,name='Publicador'),
    path('vistaautor/',views.vista_autor,name='vista_autor'),
    path('contenidos-editables/',views.vista_edicion,name='edicion'),
    path('aceptar-contenido/<int:contenido_id>/', views.aceptar_contenido, name='aceptar_contenido'),
    path('publicar-contenido/<int:contenido_id>/', views.publicar_contenido, name='publicar_contenido'),
    path('rechazar-contenido/<int:contenido_id>/', views.rechazar_contenido, name='rechazar_contenido'),
    path('articulo/<int:pk>', VistaArticulos.as_view(),name='detalles_articulo'),
    path('articulo_edicion/<int:pk>', VistaArticulosEditor.as_view(),name='detalles_articulo_edicion'),
    path('articulo_revision/<int:pk>', VistaArticulosRevision.as_view(),name='detalles_articulo_revision'),
    path('miscontenidos-borrador/',views.vista_mis_contenidos_borrador,name='ContenidosBorrador'),
    path('editar-contenido/<int:pk>/', views.EditarContenido.as_view(), name='editar_contenido'),
    path('editar-contenido-editor/<int:pk>/', views.EditarContenidoEditor.as_view(), name='editar_contenido_editor'),
    path('contenidos',VistaContenidos.as_view(),name='vistacontenidos'),
    path('categoria/<str:nombre>/', views.categoria,name='cat'),
    path('crear/',views.crear_categoria,name='Categoria'),
    path('desactivar/',views.desactivar_categoria,name='desc'),
    path('roles/',views.vista_roles, name='gestion'),
    path('asignar/',views.asignar_rol,name='asignacion'),
    path('desasignar/',views.remover_rol,name='desasignar'),
]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
