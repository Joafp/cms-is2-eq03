from django.template import Template,Context
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
def registro(request):
    return render(request,"./main/registro.html")
@login_required
def vista_login(request):
    return render(request,'./templates/registration/login.html')

