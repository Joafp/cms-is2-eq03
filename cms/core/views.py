from django.shortcuts import render, HttpResponse,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from GestionCuentas.models import UsuarioRol
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from .models import Categoria
from GestionCuentas.models import Rol,UsuarioRol
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
    categorias= Categoria.objects.filter(activo=True)
    if request.user.is_authenticated:
        usuario_rol = UsuarioRol.objects.get(username=request.user.username)
        tiene_permiso=usuario_rol.has_perm(codename="Boton desarrollador")
        context={
            'autenticado':autenticado,
            'tiene_permiso':tiene_permiso,
            'categorias': categorias
        }
    else:
        context={
            'autenticado': autenticado,
            'categorias': categorias
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

def categoria(request,nombre):
    categoria= get_object_or_404(Categoria,nombre=nombre)
    return render(request,'cat/categoria.html',{'categoria':categoria})


def crear_categoria(request):
    if request.method == 'POST':
        nombre1=request.POST['nombre']
        moderado=request.POST['moderada']
        categoria=Categoria(nombre=nombre1,moderada=moderado)
        categoria.save()
        return redirect('Administrador')
    return render(request,'crear_cat.html')


def desactivar_categoria(request):
    if request.method == 'POST':
        id_categoria= request.POST['id_categoria']
        categoria=Categoria.objects.get(id=id_categoria)
        categoria.activo=False
        categoria.save()
        return redirect('Administrador')

    return render(request, 'desactivar_cat.html')

def vista_roles(request):
    return render(request,'gestion_roles.html')


def asignar_rol(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        rol_id = request.POST.get('rol')
        usuario = UsuarioRol.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
        usuario.roles.add(rol)
        return redirect('asignacion')
    else:
        usuarios = UsuarioRol.objects.filter(usuario_activo=True)
        roles = Rol.objects.all()
        usuario_seleccionado = None
        roles_usuario = []
        roles_disponibles = []
        if 'usuario' in request.GET:
            usuario_id = request.GET.get('usuario')
            usuario_seleccionado = UsuarioRol.objects.get(id=usuario_id)
            roles_usuario = usuario_seleccionado.roles.all()
            roles_disponibles = Rol.objects.exclude(id__in=roles_usuario.values_list('id', flat=True))
        context = {
            'usuarios': usuarios,
            'roles': roles,
            'usuario_seleccionado': usuario_seleccionado,
            'roles_usuario': roles_usuario,
            'roles_disponibles': roles_disponibles
        }
        return render(request, 'asignar_rol.html', context)
    
def remover_rol(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        rol_id = request.POST.get('rol')
        usuario = UsuarioRol.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
        usuario.roles.remove(rol)
        return redirect('desasignar')
    else:
        usuarios = UsuarioRol.objects.filter(usuario_activo=True)
        usuario_seleccionado = None
        roles_usuario = []
        if 'usuario' in request.GET:
            usuario_id = request.GET.get('usuario')
            usuario_seleccionado = UsuarioRol.objects.get(id=usuario_id)
            roles_usuario = usuario_seleccionado.roles.all()
        context = {
            'usuarios': usuarios,
            'usuario_seleccionado': usuario_seleccionado,
            'roles_usuario': roles_usuario,
        }
        return render(request, 'desasignar_rol.html', context)