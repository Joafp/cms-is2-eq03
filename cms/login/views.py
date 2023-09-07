from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm
from GestionCuentas.models import UsuarioRol,Rol
from core.models import Categoria
class CustomAuthenticationForm(AuthenticationForm):
    """
    Esta clase es para customizar los mensajes de error a la hora de intentar logearse al sitio con una cuenta
    que no existe.
    error_messages = {
        'invalid_login': "Credenciales inválidas. Por favor, verifica tu usuario y contraseña.",
        'inactive': "Tu cuenta está inactiva. Contacta al administrador para más detalles.",
    }

    
    """
    error_messages = {
        'invalid_login': "Credenciales inválidas. Por favor, verifica tu usuario y contraseña.",
        'inactive': "Tu cuenta está inactiva. Contacta al administrador para más detalles.",
    }

def vista_login(request):
    """
    Esta vista nos permite verificar, primero, si el formulario es valido. En caso de ser asi
    con el metodo cleaned_data.get traemos el username y password ingresado. Luego con el metodo authenticate()
    auutenticamos el usuario.
    Si el metodo authenticate devuelve "None" significa que el usuario no esta autenticado en el sistema, en caso
    de que sea distinto nos autenticamos en el sistema y nos redirige al Menu Principal

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                print("Usuario autenticado. Redireccionando...")
                return redirect('MenuPrincipal')  # Redireccionar al menú principal
            else:
                print("Usuario no autenticado.")
        else:
            print("Formulario no válido.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None: 
                login(request, user)
                print("Usuario autenticado. Redireccionando...")
                return redirect('MenuPrincipal')  # Redireccionar al menú principal
            else:
                print("Usuario no autenticado.")
        else:
            print("Formulario no válido.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def registro(request):
    """
    Este metodo nos permite crear un formulario para que los usuarios se registren en nuestro sistema.
    Creamos un objeto UsuarioRol con los datos ingresados, siendo este un modelo creado por nosotros, explicado en models.py 
    de la app GestionCuentas
    Le asignamos el rol de Suscriptor el nuevo usuario y le registramos en el sistema.

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():

            us_rol=UsuarioRol.objects.create(
                username=form.cleaned_data.get('username'),
                email=form.cleaned_data.get('email'),
                nombres=form.cleaned_data.get('nombres'), 
                apellidos=form.cleaned_data.get('apellidos'),
            )
            rol_suscriptor, created = Rol.objects.get_or_create(nombre='Suscriptor')
            us_rol.roles.add(rol_suscriptor)
            us_rol.save()
            form.save()
            return redirect('registro')  # Redirigir a la página de inicio de sesión
    else:
        form = RegistroForm()
    return render(request, 'main/registro.html', {'form': form})
    
    """
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():

            us_rol=UsuarioRol.objects.create(
                username=form.cleaned_data.get('username'),
                email=form.cleaned_data.get('email'),
                nombres=form.cleaned_data.get('nombres'), 
                apellidos=form.cleaned_data.get('apellidos'),
            )
            rol_suscriptor, created = Rol.objects.get_or_create(nombre='Suscriptor')
            us_rol.roles.add(rol_suscriptor)
            us_rol.save()
            form.save()
            return redirect('registro')  # Redirigir a la página de inicio de sesión
    else:
        form = RegistroForm()
    return render(request, 'main/registro.html', {'form': form})

#Deslogeo
@login_required(login_url="/login")
def cerrar_sesion(request):
    """
    Este metodo nos permite cerrar sesion en el sitio.
     logout(request)
    return redirect('MenuPrincipal')

    """
    logout(request)
    return redirect('MenuPrincipal')


def vista_admin(request):
    return render (request,'admin/admin.html')



