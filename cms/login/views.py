<<<<<<< HEAD
from django.template import Template,Context
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
@login_required
def registro(request):
    return HttpResponse("hola")
def vista_login(request):
    return render(request,'./main/login.html')



=======
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render,redirect
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
>>>>>>> origin/hito1_carlosayala
