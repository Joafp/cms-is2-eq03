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
    user = User.objects.create_user(username, email, 'tu_contraseña_aqui')
    
    # Asigna el usuario al UsuarioRol
    us_rol.user = user
    us_rol.save()

if __name__ == "__main__":
    # Define los datos del usuario que deseas crear
    username = "nuevo_usuario"
    email = "nuevo_usuario@example.com"
    nombres = "Nombre"
    apellidos = "Apellido"
    
    # Llama a la función para crear el usuario
    crear_usuario(username, email, nombres, apellidos)
