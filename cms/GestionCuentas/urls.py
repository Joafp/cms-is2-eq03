from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views
from django.urls import reverse_lazy

urlpatterns = [
    path('listaUsuarios/',views.vista_lista_usuarios.as_view(), name='listaUsuarios'),
   path('editarusuario/<int:pk>/',views.vista_editar_usuario.as_view(), name='editarUsuario'),
   path('recuperarContraseña/', views.vista_recuperar_password.as_view(), name='recuperarPassword'),
   path('confirmar-recuperacion/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuario/confirmar_recuperacion.html', success_url=reverse_lazy("recuperacion_completada")), name='confirmar_recuperacion'),
    path('recuperacion-completada/', auth_views.PasswordResetCompleteView.as_view(template_name='usuario/recuperacion_completada.html'), name='recuperacion_completada'),
    path('inactivar-cuenta/<int:pk>/', views.vista_inactivar_cuenta.as_view(), name='inactivarCuenta'),
    path('redirigir-inactivar', views.redirgirInactivar, name='redirgirInactivar'),
    path('login/',include('login.urls')),
] 
