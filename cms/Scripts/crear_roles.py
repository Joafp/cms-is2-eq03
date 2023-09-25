import os
import django
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
django.setup()
from GestionCuentas.models import Rol
from django.contrib.auth.models import Permission
def crear_default_roles():
    roles=[
        {"nombre":"Autor"},
        {"nombre":"Editor"},
        {"nombre":"Publicador"},
        {"nombre":"Administrador"},
    ]
    for roles_data in roles:
        rol,crear=Rol.objects.get_or_create(nombre=roles_data["nombre"])
        if crear:
            print(f'Rol "{rol.nombre}" creado con éxito')
        else:
            print(f'El rol "{rol.nombre}" ya existe')
if __name__ == '__main__':
    crear_default_roles()
