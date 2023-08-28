from django.test import TestCase
from .models import Rol, UsuarioRol
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
class RolCrearTestCase(TestCase):
    """
    En esta prueba lo que realizamos es la creacion de un rol en nuestro sistema y comprobamos si el nombre que le asigna es el mismo
    con el cual nosotros deseamos que este
    """
    def setUp(self):
        self.crear()
    def crear(self):
       Rol.objects.create(nombre='Prueba')
    def test_nombre(self): 
        item=Rol.objects.get(nombre='Prueba')
        self.assertEqual(item.nombre,"Prueba")


# Esta prueba crea prueba a crear roles y asignar permisos
class creacionRolPermisosTest(TestCase): 
    @classmethod
    # Crea usuarios, roles y permisos para el test
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='rolsususer', password='4L1_khrSri8i')
        test_user1.save()

        test_user2 = User.objects.create_user(username='roladminuser', password='4L1_khrSri8i')
        test_user2.save()

        test_user1_rol=UsuarioRol.objects.create(
                username="rolsususer",
                email="testuser123@test.com",
                nombres="test name", 
                apellidos="test lastname",
            )
        
        test_user2_rol=UsuarioRol.objects.create(
                username="roladminuser",
                email="stafftestuser123@test.com",
                nombres="test name", 
                apellidos="test lastname",
            )
        
        # setup permisos
    
        permisos = [
            Permission.objects.get(codename="Vista autor"),
            Permission.objects.get(codename="Vista editor"),
            Permission.objects.get(codename="Vista publicador"),
            Permission.objects.get(codename="Vista administrador"),
            Permission.objects.get(codename="Boton desarrollador")
        ]
        
        rol_suscriptor=Rol.objects.create(nombre='Suscriptor')
        rol_autor=Rol.objects.create(nombre='Autor')
        rol_editor=Rol.objects.create(nombre='Editor')
        rol_publicador=Rol.objects.create(nombre='Publicador')
        rol_administrador=Rol.objects.create(nombre='Administrador')

        rol_autor.permisos.add(permisos[0], permisos[4])
        rol_editor.permisos.add(permisos[1], permisos[4])
        rol_publicador.permisos.add(permisos[2], permisos[4])
        rol_administrador.permisos.add(permisos[3], permisos[4])

        rol_suscriptor.save()
        rol_autor.save()
        rol_editor.save()
        rol_publicador.save()
        rol_administrador.save()

        test_user1_rol.roles.add(rol_suscriptor)
        test_user1_rol.save()

        test_user2_rol.roles.add(rol_suscriptor, rol_autor, rol_administrador, rol_editor, rol_publicador)
        test_user2_rol.save()

    def test_roles_asignados_correctamente(self):
        # prueba que el rol de suscriptor y los roles de desarrollo se hallan asignado correctamente
        rol_suscriptor=Rol.objects.get(nombre='Suscriptor')
        rol_autor=Rol.objects.get(nombre='Autor')
        rol_editor=Rol.objects.get(nombre='Editor')
        rol_publicador=Rol.objects.get(nombre='Publicador')
        rol_administrador=Rol.objects.get(nombre='Administrador')
        usuarioSuscriptor = UsuarioRol.objects.get(username='rolsususer')
        usuarioAministrador = UsuarioRol.objects.get(username='roladminuser')
        self.assertTrue(rol_suscriptor in usuarioSuscriptor.roles.all())
        self.assertTrue(usuarioSuscriptor.roles.count() == 1)
        self.assertTrue(usuarioAministrador.roles.count() == 5)
        self.assertTrue(rol_suscriptor in usuarioAministrador.roles.all())
        self.assertTrue(rol_autor in usuarioAministrador.roles.all())
        self.assertTrue(rol_editor in usuarioAministrador.roles.all())
        self.assertTrue(rol_publicador in usuarioAministrador.roles.all())
        self.assertTrue(rol_administrador in usuarioAministrador.roles.all())

    def test_permisos_asignados_correctamente(self):
        # prueba que los roles tengan los permisos correctos
        permisos = [
            Permission.objects.get(codename="Vista autor"),
            Permission.objects.get(codename="Vista editor"),
            Permission.objects.get(codename="Vista publicador"),
            Permission.objects.get(codename="Vista administrador"),
            Permission.objects.get(codename="Boton desarrollador")
        ]
        usuarioSuscriptor = UsuarioRol.objects.get(username='rolsususer')
        usuarioAministrador = UsuarioRol.objects.get(username='roladminuser')
        for perm in permisos:
            self.assertFalse(usuarioSuscriptor.has_perm(perm.codename))
        
        self.assertTrue(usuarioAministrador.has_perm(permisos[0].codename))
        self.assertTrue(usuarioAministrador.has_perm(permisos[1].codename))
        self.assertTrue(usuarioAministrador.has_perm(permisos[2].codename))
        self.assertTrue(usuarioAministrador.has_perm(permisos[3].codename))
        self.assertTrue(usuarioAministrador.has_perm(permisos[4].codename))