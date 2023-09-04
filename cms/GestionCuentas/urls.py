from django.urls import path,include
from . import views

urlpatterns = [
    path('listaUsuarios/',views.vista_lista_usuarios.as_view(), name='listaUsuarios'),
   path('editarusuario/<int:pk>/',views.vista_editar_usuario.as_view(), name='editarUsuario'),
   path('login/',include('login.urls')),
] 

 