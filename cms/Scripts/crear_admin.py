import os
import django
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
django.setup()
from django.contrib.auth.models import Permission,User
from GestionCuentas.models import Rol,UsuarioRol
def create_admin_role():
    # Obtener todos los permisos de superusuario
    permissions = Permission.objects.all()
    # Crear el rol de Administrador y asignarle los permisos
    admin_role, created = Rol.objects.get_or_create(nombre='Administrador')
    admin_role.permisos.set(permissions)
    admin_role.save()

    print('Rol de Administrador creado con éxito')
def asignar_rol():
    try:
        admin_rol=Rol.objects.get(nombre='Administrador')
        usuario=UsuarioRol.objects.get(username='Joaadmin')
        user=User.objects.get(username='Joaadmin')
        usuario.roles.add(admin_rol)
        user.is_superuser=True
        user.is_staff=True
        user.save()
    except Rol.DoesNotExist:
        print("Aun no fue creado el rol administrador")
    except UsuarioRol.DoesNotExist:
        print("No fue creado aun el usuario al cual asignar administrador")
        
if __name__ == '__main__':
    create_admin_role()
    asignar_rol()