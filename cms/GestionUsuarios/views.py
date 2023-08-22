from django.shortcuts import render,redirect
from .forms import RolForm
def crear_rol(request):
    if request.method=='POST':
        form =RolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Registro')
    else: 
        form= RolForm()
    return render(request,'crear_rol.html',{'form':form})
    
