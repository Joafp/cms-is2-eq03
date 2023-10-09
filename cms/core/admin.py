from django.contrib import admin
from .models import Contenido,Categoria
"""Al registrar contenido dentro de admin nos permite crear nuevos contenidos, 
directamente desde al admin de django, esto en caso de querer hacer pruebas"""
admin.site.register(Contenido)
admin.site.register(Categoria)