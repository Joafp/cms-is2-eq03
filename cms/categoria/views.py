from django.shortcuts import render,redirect
from .models import Categoria
# Create your views here.
def crear_categoria(request):
    if request.method == 'POST':
        nombre1=request.POST['nombre']
        moderado=request.POST['moderada']
        categoria=Categoria(nombre=nombre1,moderada=moderado)
        categoria.save()
        return redirect('Categoria')
    return render(request,'crear_cat.html')
