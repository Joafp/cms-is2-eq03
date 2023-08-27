from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from GestionCuentas.models import UsuarioRol
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
@never_cache
def vista_MenuPrincipal(request):
    """
    Esta vista nos permite ingresar al template del menu principal, le pasamos como contextos 
    los datos de usuario y de usuariorol en caso de que ya inicio sesion
    autenticado=User.is_authenticated
    context={
        'autenticado':autenticado,
    }
    print("Usuario: ",autenticado)
    return render(request, 'crear/main.html',context )
    """
    autenticado=User.is_authenticated
    
    if request.user.is_authenticated:
        usuario_rol = UsuarioRol.objects.get(username=request.user.username)
        context={
            'autenticado':autenticado,
            'usuario_rol': usuario_rol
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
    Nos permite redigir al usuario al template de trabajores, le pasamos como datos 
    usuario_rol debido que se utiliza en el html para sbaer que botones mostrar al usuario 
    de acuerdo a su rol
    usuario_rol = UsuarioRol.objects.get(username=request.user.username)
    return render(request,'crear/main_trabajadores.html',{'usuario_rol': usuario_rol}) 
    """
    usuario_rol = UsuarioRol.objects.get(username=request.user.username)
    return render(request,'crear/main_trabajadores.html',{'usuario_rol': usuario_rol}) 