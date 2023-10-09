from django.test import TestCase,Client
from django.urls import reverse
from . import urls
from .models import Contenido, Categoria
from GestionCuentas.models import UsuarioRol, Rol
from django.contrib.auth.models import Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from .models import Categoria,UsuarioRol,Contenido
from GestionCuentas.models import Rol
from django.test import override_settings
from django.core import mail

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
"""Nos permite comprobar si la creacion de contenidos en nuestra vista funciona"""
class CrearContenidoTestCase(TestCase):
    def setUp(self):
        self.user= User.objects.create_user(username='autor_prueba', password='4L1_khrSri8i')
        # Crea un usuario con el rol 'Autor' para usarlo como autor del contenido
        self.autor = UsuarioRol.objects.create(
            username='autor_prueba',
            email='autor@prueba.com',
            nombres='Nombre del Autor',
            apellidos='Apellido del Autor',
        )
        self.autor.roles.add(Rol.objects.create(nombre='Autor'))
        # Crea una categoría de prueba
        self.categoria = Categoria.objects.create(nombre='Categoría de Prueba')
        # Datos de ejemplo para el contenido
        self.datos_contenido = {
            'titulo': 'Título de Prueba',
            'autor': self.autor.id,
            'categoria': self.categoria.id,
            'resumen': 'Resumen de prueba',
            'cuerpo': 'Cuerpo de prueba',
        }

    def test_creacion_de_contenido(self):
        # Iniciar sesión como el usuario autor
        self.client.login(username='autor_prueba', password='4L1_khrSri8i')
        # Realiza una solicitud POST para crear el contenido utilizando la vista de creación
        response = self.client.post(reverse('crear_contenido'), self.datos_contenido, follow=True)

        # Verifica que la solicitud redirija a la página deseada después de la creación
        self.assertRedirects(response, reverse('crear_contenido'))

        # Verifica que el contenido se ha creado correctamente en la base de datos
        self.assertTrue(Contenido.objects.filter(titulo='Título de Prueba').exists())
        print(f"Contenido con título: 'Título de Prueba' creado exitosamente.") 
    def tearDown(self):
        # Limpia los datos de prueba si es necesario
        self.autor.delete()
        self.categoria.delete()
class AccesoContenidoTestCase(TestCase):
    def setUp(self):
        # Crear un contenido de prueba
        self.user = User.objects.create_user(username='autor_prueba', password='4L1_khrSri8i')
        self.autor = UsuarioRol.objects.create(
            username='autor_prueba',
            email='autor@prueba.com',
            nombres='Nombre del Autor',
            apellidos='Apellido del Autor',
        )
        self.autor.roles.add(Rol.objects.create(nombre='Autor'))
        self.autor.roles.add(Rol.objects.create(nombre='Editor'))
        self.autor.roles.add(Rol.objects.create(nombre='Publicador'))
        self.categoria = Categoria.objects.create(nombre='Categoría de Prueba')
        self.contenido = Contenido.objects.create(
            titulo='Título de Prueba',
            autor=self.autor,
            categoria=self.categoria,
            resumen='Resumen de prueba',
            cuerpo='Cuerpo de prueba',
            imagen='/contenido_imagenes/6f0c63b0-3a7d-11ee-8996-c34107379e5e.jpg'
        )

    def test_acceso_a_contenido(self):
        # Iniciar sesión como el usuario autor
        self.client.login(username='autor_prueba', password='4L1_khrSri8i')
        
        # Obtener la URL del detalle del contenido creado
        contenido_url = reverse('detalles_articulo', args=[str(self.contenido.id)])
        
        # Realizar una solicitud GET para acceder al contenido
        response = self.client.get(contenido_url)
        
        # Verificar que la solicitud sea exitosa (código 200)
        self.assertEqual(response.status_code, 200)
        print(f"Contenido con título: 'Título de Prueba' ingresado exitosamente.") 
    def test_aceptar_contenido(self):
        # Obtiene la URL para la vista aceptar_contenido utilizando reverse()
        url = reverse('aceptar_contenido', args=[self.contenido.id])

        # Realiza una solicitud HTTP GET a la URL
        response = self.client.get(url)

        # Verifica que la respuesta sea un redireccionamiento HTTP 302
        self.assertEqual(response.status_code, 302)
        print("Estado actual:", self.contenido.estado)
        self.contenido.estado='A'
        self.contenido.save()
        print("Estado luego de aceptar:", self.contenido.estado)
        # Vuelve a cargar el objeto de contenido desde la base de datos
        self.contenido.refresh_from_db()

        # Verifica que el estado del contenido se haya actualizado a 'R'
        self.assertEqual(self.contenido.estado, 'A')
    def test_rechazar_contenido(self):
          # Obtiene la URL para la vista aceptar_contenido utilizando reverse()
        url = reverse('rechazar_contenido', args=[self.contenido.id])

        # Realiza una solicitud HTTP GET a la URL
        response = self.client.get(url)

        # Verifica que la respuesta sea un redireccionamiento HTTP 302
        self.assertEqual(response.status_code, 302)
        print("Estado actual:", self.contenido.estado)
        self.contenido.estado='r'
        self.contenido.save()
        print("Estado luego de rechazar:", self.contenido.estado)
        # Vuelve a cargar el objeto de contenido desde la base de datos
        self.contenido.refresh_from_db()

        # Verifica que el estado del contenido se haya actualizado a 'R'
        self.assertEqual(self.contenido.estado, 'r')
    def test_inactivar_contenido(self):
          # Obtiene la URL para la vista aceptar_contenido utilizando reverse()
        url = reverse('inactivar_contenido', args=[self.contenido.id])

        # Realiza una solicitud HTTP GET a la URL
        response = self.client.get(url)
        print("Estado actual:", self.contenido.estado)
        # Verifica que la respuesta sea un redireccionamiento HTTP 302
        self.assertEqual(response.status_code, 302)
        self.contenido.estado='I'
        self.contenido.save()
        print("Estado luego de inactivar:", self.contenido.estado)
        # Vuelve a cargar el objeto de contenido desde la base de datos
        self.contenido.refresh_from_db()

        # Verifica que el estado del contenido se haya actualizado a 'R'
        self.assertEqual(self.contenido.estado, 'I')
    def test_publicar_contenido(self):
          # Obtiene la URL para la vista aceptar_contenido utilizando reverse()
        url = reverse('inactivar_contenido', args=[self.contenido.id])

        # Realiza una solicitud HTTP GET a la URL
        response = self.client.get(url)

        # Verifica que la respuesta sea un redireccionamiento HTTP 302
        self.assertEqual(response.status_code, 302)
        self.contenido.estado='P'
        self.contenido.save()
        # Vuelve a cargar el objeto de contenido desde la base de datos
        self.contenido.refresh_from_db()

        # Verifica que el estado del contenido se haya actualizado a 'R'
        self.assertEqual(self.contenido.estado, 'P')
    
    def tearDown(self):
        # Limpieza de datos de prueba si es necesario
        self.autor.delete()
        self.categoria.delete()

class notificacionCorreoTestCase(TestCase):
    """
        Verifica que se pueden enviar las notificaciones por correo y que se muestra el mensaje apropiado
        Fecha: 2023/10/01
    """

    def setUp(self):
        self.user = User.objects.create_user(username="TestUser", email='testuseremail@test.com', password="4L1_khrSri8i")
        self.autor = UsuarioRol.objects.create(username=self.user.username, email=self.user.email)
        self.autor.roles.add(Rol.objects.create(nombre='Autor'), Rol.objects.create(nombre='Editor'))
        self.categoria = Categoria.objects.create(nombre='Categoría de Prueba')
        self.contenido = Contenido.objects.create(
            titulo='Título de Prueba',
            autor=self.autor,
            categoria=self.categoria,
            resumen='Resumen de prueba',
        )

    def testEmailBackend(self):
        """
            Verifica que la aplicacion puede conectarse al servicio de correo
        """
        backend = mail.get_connection('django.core.mail.backends.smtp.EmailBackend')
        self.assertIsNotNone(backend, "No se pudo conectar con el servicio de correo")

    @override_settings(EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend')# El correo se mantiene en la memoria para facilitar el test
    def testEmailEdicion(self):
        """
            Verifica que se envia el mensaje correcto en el email de edicion de contenido y al email correcto
        """
        login = self.client.login(username="TestUser", password="4L1_khrSri8i")
        self.assertTrue(login, "No se pudo acceder a la pagina con las credenciales especificadas")
        response = self.client.get(reverse('editar_contenido_editor', kwargs={'pk': self.contenido.pk}))
        self.assertEqual(response.status_code, 200, "No se pudo acceder a la pagina para editar el contenido")
        form = response.context['form']
        response = self.client.post(reverse('editar_contenido_editor', kwargs={'pk': self.contenido.pk}), data={"enviar_publicador": "enviar_publicador",
                                                                                                                "titulo": "Nuevo titulo",
                                                                                                                "categoria":form['categoria'].initial,
                                                                                                                "resumen":form['resumen'].initial,
                                                                                                               })
        self.assertRedirects(response, reverse('edicion'), 302, 200, "Hubo un error al guardar la edicion")
        self.assertEqual(len(mail.outbox), 1, "No se envio el email o se envio mas de un email")
        self.assertEqual(mail.outbox[0].subject, 'Contenido editado')
        self.assertEqual(mail.outbox[0].body, f"Su contenido {form['titulo'].initial} fue editado")
        self.assertTrue("testuseremail@test.com" in mail.outbox[0].recipients(), "No se envio el email a la direccion de correo del autor")

    def testEmailRecuperacion(self):
        """
            Verifica que se envia el email de recuperacion y que es enviado a la direccion correcta
        """
        response = self.client.post(reverse('recuperarPassword'), data={'email':"testuseremail@test.com"})
        self.assertRedirects(response, reverse('MenuPrincipal'), 302, 200, "No se envio la solicitud de recuperacion")
        self.assertEqual(len(mail.outbox), 1, "No se envio el email o se envio mas de un email")
        self.assertEqual(mail.outbox[0].subject, 'CMS IS2 EQ03 - Recuperacion de contraseña')
        self.assertTrue("testuseremail@test.com" in mail.outbox[0].recipients(), "No se envio el email a la direccion correcta")
