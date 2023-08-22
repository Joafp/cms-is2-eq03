from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

@login_required(login_url="/login")
def vista_MenuPrincipal(request):
    return HttpResponse("Hola")