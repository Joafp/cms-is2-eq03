from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def vista_login(request):
    return render(request,'./templates/registration/login.html')