from django.test import TestCase,Client
from django.contrib.auth.models import User
from .models import Categoria,UsuarioRol,Contenido
from GestionCuentas.models import Rol

class CategoriaTestCase(TestCase):
    def setUp(self):
        self.client=Client()
        self.user = User.objects.create_user(username='Administrador_prueba', password='4L1_khrSri8i')
        self.admin = UsuarioRol.objects.create(
            username='Administrador_prueba',
            email='administrador@prueba.com',
            nombres='Nombre del Administrador',
            apellidos='Apellido del Administrador',
        )
        self.admin.roles.add(Rol.objects.create(nombre='Administrador'))
        self.categoria = Categoria.objects.create(nombre='Test')
        self.contenido = Contenido.objects.create(
            titulo='Título de Prueba',
            autor=self.admin,
            categoria=self.categoria,
            resumen='Resumen de prueba',
            cuerpo='Cuerpo de prueba',
        )

    def test_crear_categoria(self):
        self.client.login(username='Administrador_prueba', password='4L1_khrSri8i')
        response = self.client.post('/crear/', {'nombre': 'Nueva Categoria', 'moderada': True})
        self.assertRedirects(response, '/login/administrador/', msg_prefix='La vista de crear categoría no redirige a /administrador/')
        categoria = Categoria.objects.get(nombre='Nueva Categoria')
        self.assertTrue(categoria.moderada, 'La categoría creada no está moderada')

    def test_desactivar_categoria(self):
        self.client.login(username='Administrador_prueba', password='4L1_khrSri8i')
        response = self.client.post('/desactivar/', {'id_categoria': self.categoria.id})
        self.assertRedirects(response, '/login/administrador/', msg_prefix='La vista de desactivar categoría no redirige a /administrador/')
        categoria = Categoria.objects.get(id=self.categoria.id)
        self.assertFalse(categoria.activo, 'La categoría no está desactivada')

class RolTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='Administrador_prueba', password='4L1_khrSri8i')
        self.usuario_rol = UsuarioRol.objects.create(
            username='Administrador_prueba',
            email='administrador@prueba.com',
            nombres='Nombre del Administrador',
            apellidos='Apellido del Administrador',
        )

        self.rol_administrador = Rol.objects.create(nombre='Autor')
        self.usuario_rol.roles.add(self.rol_administrador)
        self.rol_administrador = Rol.objects.create(nombre='Editor')
        self.usuario_rol.roles.add(self.rol_administrador)
        self.rol_administrador = Rol.objects.create(nombre='Administrador')
        self.rol_test = Rol.objects.create(nombre='Test Rol')
        self.usuario_rol.roles.add(self.rol_administrador)

    def test_asignar_rol(self):
        self.client.login(username='Administrador_prueba', password='4L1_khrSri8i')
        response = self.client.post('/asignar/', {'usuario': self.usuario_rol.id, 'rol': self.rol_test.id})
        self.assertRedirects(response, '/asignar/', msg_prefix='La vista de asignar rol no redirige a /roles/')
        usuario_rol = UsuarioRol.objects.get(id=self.usuario_rol.id)
        rol = usuario_rol.roles.get(nombre=self.rol_test.nombre)
        self.assertEqual(rol.nombre, 'Test Rol', 'El rol asignado al usuario no es el rol esperado')

    def test_remover_rol(self):
        self.client.login(username='Administrador_prueba', password='4L1_khrSri8i')
        response = self.client.post('/desasignar/', {'usuario': self.usuario_rol.id, 'rol': self.rol_test.id})
        self.assertRedirects(response, '/desasignar/', msg_prefix='La vista de remover rol no redirige a /desasignar/')
        usuario_rol = UsuarioRol.objects.get(id=self.usuario_rol.id)
        rol=usuario_rol.roles.filter(nombre=self.rol_test.nombre).first()
        self.assertIsNone(rol, 'El rol no fue removido del usuario')
