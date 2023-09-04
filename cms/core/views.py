from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from GestionCuentas.models import UsuarioRol
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.views.generic import ListView, DeleteView,CreateView
from django.views.generic.detail import DetailView
from .models import Contenido
class CrearContenido(CreateView):
    model= Contenido
    template_name= 'crear_contenido.html'
    fields= '__all__'

@never_cache
def vista_MenuPrincipal(request):
    """
    Fecha documentacion: 28/08/2023
    Esta vista nos permite ingresar al template del menu principal, le pasamos como contextos 
    los datos de usuario y de usuariorol en caso de que ya inicio sesion
    autenticado=User.is_authenticated
    if request.user.is_authenticated:
        usuario_rol = UsuarioRol.objects.get(username=request.user.username)
        tiene_permiso=usuario_rol.has_perm("Boton desarrollador")
        context={
            'autenticado':autenticado,
            'tiene_permiso':tiene_permiso,
        }
    else:
        context={
            'autenticado': autenticado
        }    
    print("Usuario: ",autenticado)
    """
    autenticado=User.is_authenticated
    
    if request.user.is_authenticated:
        usuario_rol = UsuarioRol.objects.get(username=request.user.username)
        tiene_permiso=usuario_rol.has_perm("Boton desarrollador")
        context={
            'autenticado':autenticado,
            'tiene_permiso':tiene_permiso,
        }
    else:
        context={
            'autenticado': autenticado
        }    
    print("Usuario: ",autenticado)
    return render(request, 'crear/main.html',context )
@login_required(login_url="/login")
def vista_trabajador(request):
    """
    Fecha documentacion: 28/08/2023
    Nos permite redigir al usuario al template de trabajores, le pasamos como datos 
    usuario_rol debido que se utiliza en el html para sbaer que botones mostrar al usuario 
    de acuerdo a su rol
    usuario_rol = UsuarioRol.objects.get(username=request.user.username)
    return render(request,'crear/main_trabajadores.html',{'usuario_rol': usuario_rol}) 
    """
    usuario_rol = UsuarioRol.objects.get(username=request.user.username)
    return render(request,'crear/main_trabajadores.html',{'usuario_rol': usuario_rol}) 

class VistaArticulos(DetailView):
    model = Contenido
    template_name='articulo_detallado.html'
class VistaContenidos(ListView):
    model= Contenido
    template_name='Contenidos.html'

