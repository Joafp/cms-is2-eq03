from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from GestionCuentas.models import UsuarioRol
from django.contrib.auth.models import User
@login_required(login_url="/login")
def vista_MenuPrincipal(request):
    usuario_rol = UsuarioRol.objects.get(username=request.user.username)
    return render(request, 'crear/main.html', {'usuario_rol': usuario_rol})