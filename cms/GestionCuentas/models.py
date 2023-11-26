from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission, User
class PermisosPer(models.Model):
    """
    Modelo para definir permisos personalizados
    Generamos una clase PermisoPer para diferenciar los permisos que ya cuenta django con los permisos
    que nosotros cargamos en el sistema, debido a esto simplemente heradamos la clase Meta y luego agregar los permisos
    nuevos dentro del mismo, los permisos se definen con un nombre y con la descripcion de que realizara en el sistema
    """
    class Meta:
        permissions=[
            ("Boton desarrollador","Permite entrar a la vista desarrollador"),
            ("Vista_autor","Permite ingresar a la vista autor"),
            ("Vista_editor","Permite ingresar a la vista editor"),
            ("Vista_publicador","Permite ingresar a la vista publicador"),
            ("Vista_administrador","Permite ingresar a la vista administrador"),
            ("Editar usuarios", "Permite editar la informacion de usuarios"),
            ("Ver usuarios", "Permite ver la lista de usuarios"),
            ("Vista_tabla", "Permite ver la tabla general"),
            ("Publicacion no moderada", "Permite la publicacion en categorias no moderadas"),
        ]
class Rol(models.Model):
    """
    Modelo para definir roles de usuarios
    nombre: nos sirve para cargar el nombre del rol que creamos
    permisos: como vimos anteriormente se puede agregar permisos a nuestro sistema y un rol puede tener 
    mas de un permiso por lo que hicimos que sea manyyomany
    """
    nombre=models.CharField(max_length=50,unique=True)
    permisos=models.ManyToManyField(Permission,default=None)
    def __str__(self):
        return self.nombre
class UsuarioRol(AbstractBaseUser):
    """
    Modelo personalizado para usuarios con roles
    username:En este apartado guardamos el username que utiliza un nuevo usuario en su registro
    email:nos permite guardar el correo y como vamos a enviar notificaciones por correo pusimos como un atributo
    unico en nuestro sistema y tambien obligatorio
    nombres:guarda los nombres del usuario
    apellidos:Guarda los apellidos de usuario
    numero:guarda el numero de telefono del usuario
    usuario_activo: este atributo nos servira para inactivar cuentas logicamente
    usuario_administrador: nos permite agregar mas permisos a un usuario en caso que sea administrador
    roles: utilizamos la clase anteriormente mencionada para agregar los roles a un usuario, un usuario puede tener mas de un rol
    """
    # Resto del código
    username=models.CharField('Nombre de usuario',unique=True,max_length=100)
    email=models.EmailField('Correo electronico',max_length=254,unique=True)
    nombres=models.CharField('Nombres',max_length=200,blank=True,null=True)
    apellidos=models.CharField('Apellidos',max_length=200,blank=True,null=True)
    numero=models.IntegerField('Numero', blank=True,null=True)
    usuario_activo=models.BooleanField(default=True)
    usuario_administrador=models.BooleanField(default=False)
    roles=models.ManyToManyField(Rol)
    USERNAME_FIELD='username'
    REQUIRED_FIELDS=['email','nombres','apellidos']
    def __str__(self):
        return f'{self.nombres},{self.apellidos}'
    def has_perm(self, perm, obj=None):
        # Verifica si el usuario tiene el permiso específico
        return self.roles.filter(permisos__codename=perm).exists()
    def has_module_perms(self,app_label):
        return True
    @property
    def is_staff(self):
        return self.usuario_administrador
