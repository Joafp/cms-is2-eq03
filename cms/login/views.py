from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render,redirect
from django.views.decorators.cache import never_cache
from .forms import RegistroForm
from GestionCuentas.models import UsuarioRol,Rol
@never_cache
def vista_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
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

@never_cache
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():

            us_rol=UsuarioRol.objects.create(
                username=form.cleaned_data.get('username'),
                email=form.cleaned_data.get('email'),
                nombres=form.cleaned_data.get('nombres'), 
                apellidos=form.cleaned_data.get('apellidos'),
            )
            rol_suscriptor=Rol.objects.get(nombre='Suscriptor')
            us_rol.roles.add(rol_suscriptor)
            us_rol.save()
            form.save()
            return redirect('registro')  # Redirigir a la página de inicio de sesión
    else:
        form = RegistroForm()
    return render(request, 'main/registro.html', {'form': form})