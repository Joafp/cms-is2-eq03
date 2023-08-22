from django.template import Template,Context
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
@login_required
def registro(request):
    return HttpResponse("hola")
def vista_login(request):
    return render(request,'./main/login.html')



