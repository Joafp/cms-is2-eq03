from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from GestionCuentas.models import UsuarioRol
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
@never_cache
def vista_MenuPrincipal(request):
    autenticado=User.is_authenticated
    #usuario_rol = UsuarioRol.objects.get(username=request.user.username)
    context={
        'autenticado':autenticado,
    }
    print("Usuario: ",autenticado)
    return render(request, 'crear/main.html',context )
@login_required(login_url="/login")
def vista_trabajador(request):
    usuario_rol = UsuarioRol.objects.get(username=request.user.username)
    return render(request,'crear/main_trabajadores.html',{'usuario_rol': usuario_rol}) 