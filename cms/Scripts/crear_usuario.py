import os
import django
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
django.setup()
from django.contrib.auth.models import User
from GestionCuentas.models import UsuarioRol, Rol 


def crear_usuario(username, email, nombres, apellidos):
    # Crea un nuevo objeto UsuarioRol
    us_rol = UsuarioRol.objects.create(
        username=username,
        email=email,
        nombres=nombres,
        apellidos=apellidos,
    )
    
    # Obtiene o crea el rol "Suscriptor"
    rol_suscriptor, created = Rol.objects.get_or_create(nombre='Suscriptor')
    us_rol.roles.add(rol_suscriptor)
    us_rol.save()

    # Crea un usuario en el sistema
    user = User.objects.create_user(username, email, '12345678joa')
    
    # Asigna el usuario al UsuarioRol
    us_rol.user = user
    us_rol.save()
if __name__ == "__main__":
    usuarios = [
        {
            "username": "JoaAutor",
            "email": "joad28.d@outlook.com",
            "nombres": "Joaquin Autor",
            "apellidos": "Delgado"
        },
        {
            "username": "JoaEditor",
            "email": "joad.d@fpuna.edu.py",
            "nombres": "Joaquin Editor",
            "apellidos": "Delgado"
        },
        {
            "username": "JoaPublicador",
            "email": "joaneitor38@gmail.com",
            "nombres": "Joaquin Publicador",
            "apellidos": "Delgado"
        }
    ]

    for usuario_data in usuarios:
        crear_usuario(usuario_data["username"], usuario_data["email"], usuario_data["nombres"], usuario_data["apellidos"])
    for usuario_data in usuarios:
        username = usuario_data["username"]
        us_rol = UsuarioRol.objects.get(username=username)
        if "Autor" in username:
            rol_autor, created = Rol.objects.get_or_create(nombre='Autor')
            us_rol.roles.add(rol_autor)
        elif "Editor" in username:
            rol_editor, created = Rol.objects.get_or_create(nombre='Editor')
            us_rol.roles.add(rol_editor)
        elif "Publicador" in username:
            rol_publicador, created = Rol.objects.get_or_create(nombre='Publicador')
            us_rol.roles.add(rol_publicador)
        us_rol.save()