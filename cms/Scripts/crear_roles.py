import os
import django
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
django.setup()
from GestionCuentas.models import Rol
from django.contrib.auth.models import Permission

def crear_default_roles():
    roles = [
        {"nombre": "Autor", "permisos": [
            "Vista_autor",
            "Publicacion no moderada",
            "Boton desarrollador",
        ]},
        {"nombre": "Editor", "permisos": [
            "Vista_editor",
            "Vista_tabla",
            "Boton desarrollador",
        ]},
        {"nombre": "Publicador", "permisos": [
            "Vista_publicador",
            "Vista_tabla",
            "Boton desarrollador",
        ]},
        {"nombre": "Administrador", "permisos": [
            "Vista_administrador",
            "Editar usuarios",
            "Ver usuarios",
            "Vista_tabla",
            "Publicacion no moderada",
            "Boton desarrollador",
        ]},
    ]

    for roles_data in roles:
        rol, creado = Rol.objects.get_or_create(nombre=roles_data["nombre"])
        if creado:
            print(f'Rol "{rol.nombre}" creado con éxito')
        else:
            print(f'El rol "{rol.nombre}" ya existe')

        # Agregar permisos al rol
        for permiso_nombre in roles_data["permisos"]:
            permiso = Permission.objects.get(codename=permiso_nombre)
            rol.permisos.add(permiso)
            print(f'Permiso "{permiso_nombre}" agregado a "{rol.nombre}"')

if __name__ == '__main__':
    crear_default_roles()

