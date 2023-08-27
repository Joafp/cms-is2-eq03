from django.contrib import admin
from .models import Rol,UsuarioRol
"""
Al agregar rol y usuariorol mediante site.register lo que logramos es que se puedan utilizar ambos
como grupos en la interfaz de administracion de django
"""
class RolAdmin(admin.ModelAdmin):
    list_display=('nombre')
admin.site.register(Rol)
admin.site.register(UsuarioRol)