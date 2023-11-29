from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import CrearContenido,VistaArticulos,VistaContenidos
from .views import CrearContenido,VistaArticulos,VistaContenidos,VistaArticulosEditor,VistaArticulosRevision
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import admin
urlpatterns = [
    path('qr-code/<int:pk>/', views.qr_code, name='qr_code'),
    path('',views.vista_MenuPrincipal,name='MenuPrincipal'),
    path('main_trabajador/',views.vista_trabajador,name='maintrabajador'),
    path('gestioncuentas/',include('GestionCuentas.urls')),
    path('login/',include('login.urls')),
    path('estadistica_autor/',views.estadistica_autor,name='estadistica_autor'),
    #path('crearcontenido/',login_required(CrearContenido.as_view(),login_url="/login"),name='crear_contenido'),
    path('articulo/<int:pk>', login_required(VistaArticulos.as_view(),login_url="/login"),name='detalles_articulo'),
    path('crearcontenido/',CrearContenido.as_view(),name='crear_contenido'),
    path('editarcontenido/',views.vista_editor,name='Editar'),
    path('publicarcontenido/',views.vista_publicador,name='Publicador'),
    path('contenido/<int:contenido_id>/calificar/', views.calificar_contenido, name='calificar_contenido'),
    path('vistapublicador/',views.publicador,name='vista_pub'),
    path('estadisticas/',views.grafico_estadisticas,name='estadisticas'),
    path('vistaautor/',views.vista_autor,name='vista_autor'),
    path('aumentar_veces_compartido/<int:contenido_id>/', views.aumentar_veces_compartido, name='aumentar_veces_compartido'),
    path('tablageneral/',views.tabla_kanbangeneral,name='tabla_general'),
    path('tablageneralfiltrada/',views.buscar_tabla,name='tabla_general_filtrada'),
    path('tablaautorfiltrada/',views.buscar_tabla_autor,name='tabla_autor_filtrada'),
    path('contenidos-editables/',views.vista_edicion,name='edicion'),
    path('dar_favorito/<int:pk>/', views.dar_favorito, name='dar_favorito'),
    path('quitar_favorito/<int:pk>/', views.quitar_favorito, name='quitar_favorito'),
    path('publicar-contenido/<int:contenido_id>/', views.publicar_contenido, name='publicar_contenido'),
    path('rechazar-contenido/<int:contenido_id>/', views.rechazar_contenido, name='rechazar_contenido'),
    path('inactivar-contenido/<int:contenido_id>/', views.inactivar_contenido, name='inactivar_contenido'),
    path('reactivar-contenido/<int:contenido_id>/', views.reactivar_contenido, name='reactivar_contenido'),
    path('contenidos-inactivos/',views.contenidos_inactivos,name='contenidos-inactivos'),
    path('articulo/<int:pk>', VistaArticulos.as_view(),name='detalles_articulo'),
    path('toggle_destacado/<int:pk>/', views.toggle_destacado, name='toggle_destacado'),
    path('articulo_edicion/<int:pk>', VistaArticulosEditor.as_view(),name='detalles_articulo_edicion'),
    path('articulo_revision/<int:pk>', VistaArticulosRevision.as_view(),name='detalles_articulo_revision'),
    path('miscontenidos-borrador/',views.vista_mis_contenidos_borrador,name='ContenidosBorrador'),
    path('miscontenidos-rechazados/',views.vista_mis_contenidos_rechazados,name='ContenidosRechazados'),
    path('miscontenidos-publicados/',views.vista_mis_contenidos_publicados,name='ContenidosPublicados'),
    path('editar-contenido/<int:pk>/', views.EditarContenido.as_view(), name='editar_contenido'),
    path('historial-contenido/<int:contenido_id>/', views.historial_contenido, name='historial_contenido'),
    path('cambiar-version/<int:contenido_id>/', views.cambiar_version, name='cambiar_version'),
    path('aplicar-version/<int:contenido_id>/<int:version_id>/', views.aplicar_version, name='aplicar_version'),
    path('aceptar-rechazo-contenido/<int:contenido_id>/', views.aceptar_rechazo_contenido, name='aceptar-rechazo_contenido'),
    path('editar-contenido-editor/<int:pk>/', views.EditarContenidoEditor.as_view(), name='editar_contenido_editor'),
    path('enviar-contenido-autor/<int:pk>/', views.EnviarContenidoAutor.as_view(), name='enviar_contenido_autor'),
    path('enviar-contenido-editor/<int:pk>/', views.EnviarContenidoEditor.as_view(), name='enviar_contenido_editor'),
    path('rechazar-contenido-editor/<int:pk>/', views.RechazarContenidoEditor.as_view(), name='rechazar_contenido_editor'),
     path('rechazar-contenido-publicador/<int:pk>/', views.RechazarContenidoPublicador.as_view(), name='rechazar_contenido_publicador'),
    path('contenidos',VistaContenidos.as_view(),name='vistacontenidos'),
    path('categoria/<str:nombre>/', views.categoria,name='cat'),
    path('crear/',views.crear_categoria,name='Categoria'),
    path('desactivar/',views.desactivar_categoria,name='desc'),
    path('roles/',views.vista_roles, name='gestion'),
    path('asignar/',views.asignar_rol,name='asignacion'),
    path('desasignar/',views.remover_rol,name='desasignar'),
    path('admin/', admin.site.urls),
    path('tabla/',views.tabla_kanban,name='Tabla'),
    path('articulo/<int:pk>/like', views.dar_like, name='dar_like'),
    path('articulo/<int:pk>/dislike', views.dar_dislike, name='dar_dislike'),
    path('articulo/<int:pk>/reportar', views.ReportarContenido.as_view(), name='reportar_contenido'),
    path('reportes/', views.ListaReportes.as_view(), name='contenidos_reportados'),
    path('crear-rol/', views.CrearRol.as_view(), name='crear_rol'),
    path('editar-rol/<int:pk>/', views.EditarRol.as_view(), name='editar_rol'),
    path('desactivar-rol/<int:pk>/', views.EliminarRol.as_view(), name='desactivar_rol'),
    path('seleccionar-rol/', views.seleccionar_rol, name='seleccionar_rol'),
    path('pasar_a_borrador_contenido/<int:contenido_id>/',views.pasar_a_borrador_contenido,name='pasar_a_borrador_contenido')
]
"""Nos permite vincular la direccion donde tenemos guardadas nuestras imagenes, en este caso
tenemos las imagenes en la carpeta raiz y esta esta definida en el archivo settings"""
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
