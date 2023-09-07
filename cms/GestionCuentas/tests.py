from django.test import TestCase
from .models import Rol, UsuarioRol, PermisosPer
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.urls import reverse
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
    """
    Prueba de funcionamiento de la creacion de roles y asignacion de permisos
    Fecha: 2023/08/28
    """
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
        """
        Probamos que los roles se hayan asignado correctamente
        Fecha: 2023/08/28
        """
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
        """
        Probamos los roles asignados anteeriormente, con las distintas vistas
        Fecha: 2023/08/28
        """
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

class userAccountTest(TestCase):
    """
    Una clase para generalizar la creacion de usuarios para tests, crea un usuario con rol suscriptor y uno con rol administrador
    Fecha: 2023/09/07
    """
    userSUS = {'username':'rolsususer', 'password':'4L1_khrSri8i'}
    userADM = {'username':'roladminuser', 'password':'4L1_khrSri8i'}
    @classmethod
    def setUp(self):
        test_user1 = User.objects.create_user(username='rolsususer', password='4L1_khrSri8i')
        test_user2 = User.objects.create_user(username='roladminuser', password='4L1_khrSri8i')

        test_user1_rol=UsuarioRol.objects.create(
                username="rolsususer",
                email="testuser123@test.com",
                nombres="test name", 
                apellidos="test lastname",
                numero=1234
            )
        
        test_user2_rol=UsuarioRol.objects.create(
                username="roladminuser",
                email="stafftestuser123@test.com",
                nombres="admin name", 
                apellidos="admin lastname",
                numero=5678
            )
        
        # setup permisos
    
        permisos = [
            Permission.objects.get(codename="Vista autor"),
            Permission.objects.get(codename="Vista editor"),
            Permission.objects.get(codename="Vista publicador"),
            Permission.objects.get(codename="Vista administrador"),
            Permission.objects.get(codename="Boton desarrollador"),
            Permission.objects.get(codename="Ver usuarios"),
            Permission.objects.get(codename="Editar usuarios"),

        ]

        rol_suscriptor=Rol.objects.create(nombre='Suscriptor')
        rol_autor=Rol.objects.create(nombre='Autor')
        rol_editor=Rol.objects.create(nombre='Editor')
        rol_publicador=Rol.objects.create(nombre='Publicador')
        rol_administrador=Rol.objects.create(nombre='Administrador')

        rol_autor.permisos.add(permisos[0], permisos[4])
        rol_editor.permisos.add(permisos[1], permisos[4])
        rol_publicador.permisos.add(permisos[2], permisos[4])
        rol_administrador.permisos.add(permisos[3], permisos[4], permisos[5], permisos[6])

        rol_suscriptor.save()
        rol_autor.save()
        rol_editor.save()
        rol_publicador.save()
        rol_administrador.save()

        test_user1_rol.roles.add(rol_suscriptor)
        test_user1_rol.save()

        test_user2_rol.roles.add(rol_suscriptor, rol_autor, rol_administrador, rol_editor, rol_publicador)
        test_user2_rol.save()

class inactivacionTest(userAccountTest): 
    """
    Prueba de la inactivacion de cuentas
    Fecha: 2023/09/07
    """

    def test_inactivar_cuenta_propia(self):
        """
        Probamos que no se puede desactivar una cuenta que no es la propia
        Fecha: 2023/09/07
        """
        login = self.client.login(username=self.userSUS['username'], password=self.userSUS['password'])
        self.assertTrue(login, 'No se ha podido hacer login del usuario')
        idusuario = UsuarioRol.objects.get(username=self.userSUS['username']).pk
        response = self.client.get(reverse('inactivarCuenta', kwargs={'pk':idusuario}))
        self.assertEqual(response.status_code, 200, f'No se ha podido acceder al url {response.request["PATH_INFO"]}')
        for otheruser in UsuarioRol.objects.exclude(username=self.userSUS['username']):
            response = self.client.get(reverse('inactivarCuenta', kwargs={'pk':otheruser.pk}))
            self.assertNotEqual(response.status_code, 200, f'El usuario con id{idusuario} pudo acceder al enlace de inactivacion del usuario con id{otheruser.pk}')

    def test_cuenta_inactivada(self):
        """
        Probamos que las cuentas se inactiven correctamente y no se permita su uso posterior
        Fecha: 2023/09/07
        """
        login = self.client.login(username=self.userSUS['username'], password=self.userSUS['password'])
        self.assertTrue(login, 'No se ha podido hacer login del usuario')
        idusuario = UsuarioRol.objects.get(username=self.userSUS['username']).pk
        response = self.client.get(reverse('inactivarCuenta', kwargs={'pk':idusuario}))
        self.assertEqual(response.status_code, 200, f'No se ha podido acceder al url de inactivacion: {response.request["PATH_INFO"]}')
        response = self.client.post(reverse('inactivarCuenta', kwargs={'pk':idusuario}), {'usuario_activo':False})
        self.assertRedirects(response, reverse('MenuPrincipal'), 302, 200, 'No se ha finalizado la inactivacion')
        login = self.client.login(username=self.userSUS['username'], password=self.userSUS['password'])
        self.assertFalse(login, 'El usuario inactivado se pudo loguear en el sistema')

class recuperacionTest(TestCase):
    """
    Prueba de la recuperacion de cuentas, como es manejado por django solo se comprueban que los templates esten asociados correctamente
    Fecha: 2023/09/07
    """
    def test_templates_recuperar_password(self):
        response = self.client.get(reverse('recuperarPassword'))
        self.assertTemplateUsed(response, "usuario/recuperar_password.html", 'No se utiliza el template para el formulario de solicitud de recuperacion')
        response = self.client.get(reverse('confirmar_recuperacion', kwargs={'uidb64':'x', 'token':'x'}))
        self.assertTemplateUsed(response, "usuario/confirmar_recuperacion.html", 'No se utiliza el template para el link de recuperacion')
        response = self.client.get(reverse('recuperacion_completada'))
        self.assertTemplateUsed(response, "usuario/recuperacion_completada.html", 'No se utiliza el template al finalizar la recuperacion')


class editarCuentaTest(userAccountTest):
    """
    Prueba de la edicion de cuentas de usuario por un administrador
    Fecha: 2023/09/07
    """
    def test_sin_permisos(self):
        """
        Prueba que un usuario sin permiso no pueda ver ni editar cuentas
        """
        login = self.client.login(username=self.userSUS['username'], password=self.userSUS['password'])
        self.assertTrue(login, 'No se pudo hacer login del usuario')
        response = self.client.get(reverse('listaUsuarios'))
        self.assertNotEqual(response.status_code, 200, 'Un usuario sin permisos pudo acceder a la lista de usuarios')
        for usuario in UsuarioRol.objects.all():
            response = self.client.get(reverse('editarUsuario', kwargs={'pk':usuario.pk}))
            self.assertNotEqual(response.status_code, 200, 'Un usuario sin permisos pudo acceder a la edicion de un usuario')

    def test_con_permisos(self):
        """
        Prueba que un usuario con permisos pueda ver y editar cuentas
        """
        login = self.client.login(username=self.userADM['username'], password=self.userADM['password'])
        self.assertTrue(login, 'No se pudo hacer login del usuario')
        response = self.client.get(reverse('listaUsuarios'))
        self.assertEqual(response.status_code, 200, f'Un usuario con permisos no pudo acceder a la lista de usuarios')
        for usuario in UsuarioRol.objects.all():
            response = self.client.get(reverse('editarUsuario', kwargs={'pk':usuario.pk}))
            self.assertEqual(response.status_code, 200, 'Un usuario con permisos no pudo acceder a la edicion de un usuario')

    def test_formulario_editar_usuario(self):
        """
        Prueba que el formulario de edicion de usuario tenga los campos requeridos
        """
        login = self.client.login(username=self.userADM['username'], password=self.userADM['password'])
        self.assertTrue(login, 'No se pudo hacer login del usuario')
        usuario = UsuarioRol.objects.get(username=self.userSUS['username'])
        response = self.client.get(reverse('editarUsuario', kwargs={'pk': usuario.pk}))
        form = response.context['form']
        for field in ["username", "email", "nombres", "apellidos", "numero", "usuario_activo", "usuario_administrador", "roles"]:
            self.assertTrue( field in form.fields)
