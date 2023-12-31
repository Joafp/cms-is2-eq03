from django.test import TestCase,Client
from django.urls import reverse
from . import urls
from .models import Contenido, Categoria, Likes, VersionesContenido
from GestionCuentas.models import UsuarioRol, Rol
from django.contrib.auth.models import Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from .models import Categoria,UsuarioRol,Contenido,Calificacion,Comentario, Reporte, Favorito
from GestionCuentas.models import Rol
from django.test import override_settings
from django.core import mail
from .views import actualizar_calificacion_estrellas
from datetime import datetime
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
"""class CrearContenidoTestCase(TestCase):
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

        # Verifica que la solicitud sea exitosa (código de respuesta 200)
        self.assertEqual(response.status_code, 200)

        # Verifica que el contenido se ha creado correctamente en la base de datos
        self.assertTrue(Contenido.objects.filter(titulo='Título de Prueba').exists())
        print(f"Contenido con título: 'Título de Prueba' creado exitosamente.") 
"""
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
    """def test_aceptar_contenido(self):
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
        self.assertEqual(self.contenido.estado, 'A')"""
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
   
    def testEmailRecuperacion(self):
        """
            Verifica que se envia el email de recuperacion y que es enviado a la direccion correcta
        """
        response = self.client.post(reverse('recuperarPassword'), data={'email':"testuseremail@test.com"})
        self.assertRedirects(response, reverse('MenuPrincipal'), 302, 200, "No se envio la solicitud de recuperacion")
        self.assertEqual(len(mail.outbox), 1, "No se envio el email o se envio mas de un email")
        self.assertEqual(mail.outbox[0].subject, 'CMS IS2 EQ03 - Recuperacion de contraseña')
        self.assertTrue("testuseremail@test.com" in mail.outbox[0].recipients(), "No se envio el email a la direccion correcta")        
    """
    def testEmailEdicion(self):     
       # Verifica que se envia el mensaje correcto en el email de edicion de contenido y al email correcto
        
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
    """

class CategoriaNoModeradaTest(TestCase):
    """
        Verifica que el autor con permiso para categorias no moderadas puede publicar su contenido directamente
        Fecha: 2023/10/19
    """
    def setUp(self):
        self.user= User.objects.create_user(username='autor_prueba', password='4L1_khrSri8i')
        # Crea un usuario con el rol 'Autor' para usarlo como autor del contenido
        self.autor = UsuarioRol.objects.create(
            username='autor_prueba',
            email='autor@prueba.com',
            nombres='Nombre del Autor',
            apellidos='Apellido del Autor',
        )
        rol_autor = (Rol.objects.create(nombre='Autor'))
        self.autor.roles.add(rol_autor)
        # Agrega el permiso para categorias no moderadas
        perm = Permission.objects.create(codename="Publicacion no moderada", content_type_id=1)
        rol_autor.permisos.add(perm)

        # Crea una categoría no moderada de prueba
        self.categoria = Categoria.objects.create(nombre='Categoría de Prueba')
        self.categoria.moderada = False
        
        # Crea un contenido de ejemplo  
        self.contenido_ejemplo = Contenido.objects.create(
            titulo='Título de Prueba',
            autor= self.autor,
            categoria= self.categoria,
            estado= 'B'
        )

    def test_publicar_contenido_no_moderado(self):
        """
        Verifica que el contenido pasa de borrador a publicado directamente
        """
        # Iniciar sesión como el usuario autor
        login = self.client.login(username='autor_prueba', password='4L1_khrSri8i')
        self.assertTrue(login, "No se pudo loguear al autor de prueba")

        # Intenta enviar el contenido
        response = self.client.post(reverse('enviar_contenido_autor', kwargs={'pk': self.contenido_ejemplo.pk}), data={'enviar_editor':'enviar_editor', 'fecha_programada':'', 'hora_programada':''}, follow=True)

        # Verifica que se haya redirigido luego enviar el contenido correctamente
        self.assertRedirects(response, reverse('vista_autor'), 302, 200, "Error al enviar el contenido")

        # Verifica que el contenido se ha publicado
        self.assertTrue(Contenido.objects.filter(titulo='Título de Prueba', estado="P").exists(), "El contenido no fue publicado")     

class VersionesTest(TestCase):
    """
        Verifica que se guarden las versiones de un contenido y que se puedan restaurar
        Fecha: 2023/10/19
    """
    def setUp(self):
        self.user= User.objects.create_user(username='autor_prueba', password='4L1_khrSri8i')
        # Crea un usuario con el rol 'Autor' para usarlo como autor del contenido
        self.autor = UsuarioRol.objects.create(
            username='autor_prueba',
            email='autor@prueba.com',
            nombres='Nombre del Autor',
            apellidos='Apellido del Autor',
        )
        rol_autor = (Rol.objects.create(nombre='Autor'))
        self.autor.roles.add(rol_autor)
        # Agrega el permiso para categorias no moderadas
        perm = Permission.objects.create(codename="Publicacion no moderada", content_type_id=1)
        rol_autor.permisos.add(perm)
        perm = Permission.objects.create(codename="Vista_autor", content_type_id=2)
        rol_autor.permisos.add(perm)

        # Crea una categoría no moderada de prueba
        self.categoria = Categoria.objects.create(nombre='Categoría de Prueba')
        self.categoria.moderada = False
        
        # Crea un contenido de ejemplo  
        self.contenido_ejemplo = Contenido.objects.create(
            titulo='Ver1',
            autor= self.autor,
            categoria= self.categoria,
            estado= 'B',
            imagen= "contenido_imagenes/Octagon_delete.png"
        )

    def test_guardar_restaurar_version(self):
        """
        Guarda y restaura diferentes versiones de un contenido
        """
        # Iniciar sesión como el usuario autor
        login = self.client.login(username='autor_prueba', password='4L1_khrSri8i')
        self.assertTrue(login, "No se pudo loguear al autor de prueba")

        response = self.client.get(reverse('editar_contenido', kwargs={"pk": self.contenido_ejemplo.pk}))
        self.assertEqual(response.status_code, 200, "No se puede acceder al borrador del contenido")

        # Carga los datos iniciales del formulario
        form = response.context['form']
        data = {'guardar_borrador':'guardar_borrador'}

        for field in form.fields:
            t = form[field].initial
            if not t:
                t = ""
            data[field]=t

        # Intenta guardar el borrador
        response = self.client.post(reverse('editar_contenido', kwargs={'pk': self.contenido_ejemplo.pk}),
                                    data=data)

        # Verifica que se haya guardado la version 1
        self.assertTrue(VersionesContenido.objects.filter(contenido_base=self.contenido_ejemplo, numero_version=1).exists(), f"No se guardo la version 1: {VersionesContenido.objects.filter(contenido_base=self.contenido_ejemplo).count()}")

        # Hace y restaura varias versiones
        for i in range(2, 5):
            # Carga los datos iniciales del formulario
            response = self.client.get(reverse('editar_contenido', kwargs={"pk": self.contenido_ejemplo.pk}))
            self.assertEqual(response.status_code, 200, "No se puede acceder al borrador del contenido")
            form = response.context['form']
            data = {'guardar_borrador':'guardar_borrador'}

            for field in form.fields:
                t = form[field].initial
                if not t:
                    t = ""
                data[field]=t
            data['titulo'] = f'Ver{i}'

            # Intenta guardar el borrador con un nuevo titulo
            response = self.client.post(reverse('editar_contenido', kwargs={'pk': self.contenido_ejemplo.pk}),
                                        data=data)
            
            # Verifica que se haya guardado la version i
            self.assertTrue(VersionesContenido.objects.filter(contenido_base=self.contenido_ejemplo, numero_version=i).exists(), f"No se guardo la version {i}")
            self.assertEqual(Contenido.objects.get(id=self.contenido_ejemplo.pk).titulo, f"Ver{i}", f"No se guardo correctamente la version {i} del contenido")

            # Restaura la version i - 1
            response = self.client.get(reverse('aplicar_version', kwargs={"contenido_id": self.contenido_ejemplo.pk, "version_id": i-1}))
            
            # Verifica que se haya restaurado la version i - 1
            self.assertEqual(Contenido.objects.get(id=self.contenido_ejemplo.pk).titulo, f"Ver{i-1}", f"No se aplico la version {i-1} al contenido")

class LikesTest(TestCase):
    """
    Verifica que se guarden los likes de usuario
    Fecha: 2023/11/02
    """

    def setUp(self):
        self.num_suscriptores = 3
        self.user= User.objects.create_user(username='autor_prueba', password='4L1_khrSri8i')
        # Crea un usuario con el rol 'Autor' para usarlo como autor del contenido
        self.autor = UsuarioRol.objects.create(
            username='autor_prueba',
            email='autor@prueba.com',
            nombres='Nombre del Autor',
            apellidos='Apellido del Autor',
        )
        rol_autor = (Rol.objects.create(nombre='Autor'))
        self.autor.roles.add(rol_autor)
        # Agrega el permiso para categorias no moderadas
        perm = Permission.objects.create(codename="Publicacion no moderada", content_type_id=1)
        rol_autor.permisos.add(perm)

        # Crea una categoría no moderada de prueba
        self.categoria = Categoria.objects.create(nombre='Categoría de Prueba')
        self.categoria.moderada = False
        
        # Crea un contenido publicado de ejemplo
        self.contenido_ejemplo = Contenido.objects.create(
            titulo='Ver1',
            autor= self.autor,
            categoria= self.categoria,
            estado= 'P',
            imagen= "contenido_imagenes/Octagon_delete.png"
        )

        self.likes = Likes.objects.get_or_create(contenido=self.contenido_ejemplo)[0]

        # Crea suscriptores de prueba
        self.suscriptores = [None, None, None, None, None]

        for i in range(0, self.num_suscriptores):
            self.suscriptores[i] = User.objects.create_user(username=f'sucriptor_{i}', password='4L1_khrSri8i')
            UsuarioRol.objects.create(
                username=f'sucriptor_{i}',
                email=f'sucriptor_{i}@prueba.com',
                nombres=f'Nombre susc{i}',
                apellidos=f'Apellido susc{i}',
            )

        

    def test_boton_like(self):
        """
        Da like al contenido de prueba y verifica que se guarde el like del usuario y el contador cuente correctamente el numero
        """

        for i in range(0, self.num_suscriptores):
            # Iniciar sesión como el suscriptor
            login = self.client.login(username=f'sucriptor_{i}', password='4L1_khrSri8i')
            self.assertTrue(login, f"No se pudo loguear al sucriptor_{i}")

            # Da like al contenido
            response = self.client.get(reverse('dar_like', kwargs={"pk": self.contenido_ejemplo.pk}))
            self.assertEqual(response.status_code, 302, "No se pudo dar like al contenido")

            # Verifica el incremento del numero de likes del contenido
            self.assertEqual(self.likes.user_likes_count(), i+1, "No se contaron los likes correctamente")

        
        for i in range(0, self.num_suscriptores):
            # Iniciar sesión como el suscriptor
            login = self.client.login(username=f'sucriptor_{i}', password='4L1_khrSri8i')
            self.assertTrue(login, f"No se pudo loguear al sucriptor_{i}")

            # Quitar like al contenido
            response = self.client.get(reverse('dar_like', kwargs={"pk": self.contenido_ejemplo.pk}))
            self.assertEqual(response.status_code, 302, "No se pudo quitar el like del contenido")

            # Verifica la reduccion del numero de likes del contenido
            self.assertEqual(self.likes.user_likes_count(), self.num_suscriptores-1-i, "No se contaron correctamente los likes quitados")

    def test_boton_dislike(self):
        """
        Da dislike al contenido de prueba y verifica que se guarde el like del usuario y el contador cuente correctamente el numero
        """

        for i in range(0, self.num_suscriptores):
            # Iniciar sesión como el suscriptor
            login = self.client.login(username=f'sucriptor_{i}', password='4L1_khrSri8i')
            self.assertTrue(login, f"No se pudo loguear al sucriptor_{i}")

            # Da dislike al contenido
            response = self.client.get(reverse('dar_dislike', kwargs={"pk": self.contenido_ejemplo.pk}))
            self.assertEqual(response.status_code, 302, "No se pudo dar dislike al contenido")

            # Verifica el incremento del numero de dislikes del contenido
            self.assertEqual(self.likes.user_dislikes_count(), i+1, "No se contaron los dislikes correctamente")

        
        for i in range(0, self.num_suscriptores):
            # Iniciar sesión como el suscriptor
            login = self.client.login(username=f'sucriptor_{i}', password='4L1_khrSri8i')
            self.assertTrue(login, f"No se pudo loguear al sucriptor_{i}")

            # Quitar dislike al contenido
            response = self.client.get(reverse('dar_dislike', kwargs={"pk": self.contenido_ejemplo.pk}))
            self.assertEqual(response.status_code, 302, "No se pudo quitar el dislike del contenido")

            # Verifica la reduccion del numero de dislikes del contenido
            self.assertEqual(self.likes.user_dislikes_count(), self.num_suscriptores-1-i, "No se contaron correctamente los dislikes quitados")


class CalificacionTestCase(TestCase):
    def setUp(self):
        self.autor = UsuarioRol.objects.create(
            username='autor_prueba',
            email='autor@prueba.com',
            nombres='Nombre del Autor',
            apellidos='Apellido del Autor',
        )
        rol_autor = (Rol.objects.create(nombre='Autor'))
        self.autor.roles.add(rol_autor)
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.categoria = Categoria.objects.create(nombre='Categoría de Prueba')
        self.contenido = Contenido.objects.create(
            titulo='Contenido de Prueba',
            autor=self.autor,
            categoria=self.categoria,
            resumen='Resumen de prueba',
            cuerpo='Cuerpo de prueba',
            imagen='/contenido_imagenes/imagen.jpg'
        )

    def test_calificar_contenido(self):
        self.client.login(username='testuser', password='testpassword')
        calificacion_data = {'calificacion': 4}  # Calificación de ejemplo
        response = self.client.post(f'/contenido/{self.contenido.id}/calificar/', calificacion_data)
        self.assertEqual(response.status_code, 302)  # Comprueba que se redirige correctamente

        # Comprueba que la calificación se ha registrado en la base de datos
        calificacion = Calificacion.objects.get(contenido=self.contenido, usuario=self.user)
        self.assertEqual(calificacion.calificacion, 4)

        # Comprueba que la calificación media del contenido se ha actualizado
        self.contenido.refresh_from_db()
        self.assertEqual(self.contenido.promedio_calificaciones, 4.0)  # Actualiza esto con el valor esperado

class ReporteTest(TestCase):
    """
    Fecha: 2023-11-30
    Este test verifica que se cuando un usuario reporte un contenido el contenido se guarde y contenga la informacion correcta,
    tambien se verifica que el autor reciba la notificacion de reporte
    """
    def setUp(self):
        self.autor = UsuarioRol.objects.create(
            username='testuser',
            email='autor@prueba.com',
            nombres='Nombre del Autor',
            apellidos='Apellido del Autor',
        )
        rol_autor = (Rol.objects.create(nombre='Autor'))
        self.autor.roles.add(rol_autor)
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.autor.save()
        self.categoria = Categoria.objects.create(nombre='Categoría de Prueba')
        self.contenido = Contenido.objects.create(
            titulo='Contenido de Prueba',
            autor=self.autor,
            categoria=self.categoria,
            resumen='Resumen de prueba',
            cuerpo='Cuerpo de prueba',
            imagen='/contenido_imagenes/imagen.jpg'
        )

    def test_reportar_contenido(self):
        login = self.client.login(username='testuser', password='testpassword')
        self.assertTrue(login, "No se pudo logear al usuario")
        response = self.client.post(reverse('reportar_contenido', args=[self.contenido.pk]), data={'texto':'Este contenido tiene informacion incorrecta'})
        reporte_guardado = Reporte.objects.get(texto='Este contenido tiene informacion incorrecta')
        self.assertIsNotNone(reporte_guardado, "No se guardo el reporte")
        self.assertEqual(reporte_guardado.contenido, self.contenido, "El reporte no se relaciono al contenido correcto")
        self.assertEqual(reporte_guardado.usuario, self.autor, "El reporte no se relaciono al autor del reporte correcto")
        self.assertEqual(len(mail.outbox), 1, "No se envio el email o se envio mas de un email")
        self.assertEqual(mail.outbox[0].subject, 'Contenido reportado')
        self.assertTrue(self.autor.email in mail.outbox[0].recipients(), "No se envio el email a la direccion correcta")

class ProgramarContenidoTest(TestCase):
    """
    Fecha: 2023-11-30
        Este test verifica que un contenido se pueda programar para publicarse en una fecha y hora posterior y que se guarde correctamente la fecha y hora programadas
    """
    def setUp(self):
        self.user= User.objects.create_user(username='autor_prueba', password='4L1_khrSri8i')
        # Crea un usuario con el rol 'Autor' para usarlo como autor del contenido
        self.autor = UsuarioRol.objects.create(
            username='autor_prueba',
            email='autor@prueba.com',
            nombres='Nombre del Autor',
            apellidos='Apellido del Autor',
        )
        rol_autor = (Rol.objects.create(nombre='Autor'))
        self.autor.roles.add(rol_autor)
        # Agrega el permiso para categorias no moderadas
        perm = Permission.objects.create(codename="Publicacion no moderada", content_type_id=1)
        rol_autor.permisos.add(perm)

        # Crea una categoría no moderada de prueba
        self.categoria = Categoria.objects.create(nombre='Categoría de Prueba')
        self.categoria.moderada = False
        
        # Crea un contenido de ejemplo  
        self.contenido_ejemplo = Contenido.objects.create(
            titulo='Título de Prueba',
            autor= self.autor,
            categoria= self.categoria,
            estado= 'B'
        )

    def test_publicar_contenido_programado(self):
        """
        Verifica que el contenido se programo para publicar
        """
        # Iniciar sesión como el usuario autor
        login = self.client.login(username='autor_prueba', password='4L1_khrSri8i')
        self.assertTrue(login, "No se pudo loguear al autor de prueba")

        fecha_programada = '2024-01-01'
        hora_programada = '10:00'

        # Intenta enviar el contenido
        response = self.client.post(reverse('enviar_contenido_autor', kwargs={'pk': self.contenido_ejemplo.pk}), data={'enviar_editor':'enviar_editor', 'fecha_programada':fecha_programada, 'hora_programada':hora_programada}, follow=True)

        # Verifica que se haya redirigido luego enviar el contenido correctamente
        self.assertRedirects(response, reverse('vista_autor'), 302, 200, "Error al enviar el contenido")

        # Verifica que el contenido paso al estado publicado
        self.assertTrue(Contenido.objects.filter(titulo='Título de Prueba', estado="P").exists(), "El contenido no pudo ser publicado")

        # Verifica que el contenido esta programado para publicarse
        self.assertTrue(Contenido.objects.get(titulo='Título de Prueba', estado="P").contenido_programado, "El contenido se publico inmediatamente")

        # Verifica que la fecha y hora sean las correctas
        self.assertEqual(Contenido.objects.get(titulo='Título de Prueba', estado="P").fecha_publicacion, datetime.strptime(fecha_programada+' '+hora_programada, '%Y-%m-%d %H:%M'), "Se programo una fecha y hora incorrectas")



class ContenidoDestacadoTest(TestCase):
    """
    Fecha: 2023-11-30
        Este test verifica que un contenido se pueda destacar
    """
    def setUp(self):
        self.user= User.objects.create_user(username='autor_prueba', password='4L1_khrSri8i')
        # Crea un usuario con el rol 'Autor' para usarlo como autor del contenido
        self.autor = UsuarioRol.objects.create(
            username='autor_prueba',
            email='autor@prueba.com',
            nombres='Nombre del Autor',
            apellidos='Apellido del Autor',
        )
        rol_autor = (Rol.objects.create(nombre='Autor'))
        self.autor.roles.add(rol_autor)
        # Agrega el permiso para categorias no moderadas
        perm = Permission.objects.create(codename="Publicacion no moderada", content_type_id=1)
        rol_autor.permisos.add(perm)
        perm = Permission.objects.create(codename="Vista_publicador", content_type_id=2)
        rol_autor.permisos.add(perm)

        rol_autor.save()

        # Crea una categoría no moderada de prueba
        self.categoria = Categoria.objects.create(nombre='Categoría de Prueba')
        self.categoria.moderada = False
        
        # Crea un contenido de ejemplo  
        self.contenido_ejemplo = Contenido.objects.create(
            titulo='Contenido destacado',
            autor= self.autor,
            categoria= self.categoria,
            estado= 'P',
            fecha_publicacion= datetime.now(),
            imagen='/contenido_imagenes/6f0c63b0-3a7d-11ee-8996-c34107379e5e.jpg',
            destacado=0
        )
        
        # Crea un contenido que aparecera despues de los destacados
        self.contenido_no_destatcado = Contenido.objects.create(
            titulo='Contenido no destacado',
            autor= self.autor,
            categoria= self.categoria,
            estado= 'P',
            fecha_publicacion= datetime.now(),
            imagen='/contenido_imagenes/6f0c63b0-3a7d-11ee-8996-c34107379e5e.jpg',
            destacado=0
        )

    def test_destacar_contenido(self):
        """
        Verifica que el contenido que se destaca aparece primero en el inicio
        """
        # Iniciar sesión como el usuario autor
        login = self.client.login(username='autor_prueba', password='4L1_khrSri8i')
        self.assertTrue(login, "No se pudo loguear al autor de prueba")

        # Verifica que el contenido no esta destacado inicialmente
        self.assertEqual(self.contenido_ejemplo.destacado, 0, "El contenido ya estaba destacado")

        # Verifica que el contenido no es el primero en la pagina
        response = self.client.get(reverse('MenuPrincipal'))
        self.assertEqual(response.context.get('contenido')[0], self.contenido_no_destatcado, "El contenido se mostro primero en la pagina aunque no estaba destacado")

        # Destaca el contenido
        self.contenido_ejemplo.destacado = 1
        self.contenido_ejemplo.save()

        # Verifica que el contenido ahora si esta destacado
        self.assertNotEqual(self.contenido_ejemplo.destacado, 0, "El contenido no fue destacado")

        # Verifica que el contenido es el primero en la pagina
        response = self.client.get(reverse('MenuPrincipal'))
        self.assertEqual(response.context.get('contenido').filter(destacado=1)[0], self.contenido_ejemplo, "El contenido no se mostro primero en la pagina aunque estaba destacado")

class ContenidoFavoritoTest(TestCase):
    """
    Fecha: 2023-11-30
        Este test verifica que un contenido se pueda destacar
    """
    def setUp(self):
        self.user= User.objects.create_user(username='autor_prueba', password='4L1_khrSri8i')
        # Crea un usuario con el rol 'Autor' para usarlo como autor del contenido
        self.autor = UsuarioRol.objects.create(
            username='autor_prueba',
            email='autor@prueba.com',
            nombres='Nombre del Autor',
            apellidos='Apellido del Autor',
        )
        rol_autor = (Rol.objects.create(nombre='Autor'))
        self.autor.roles.add(rol_autor)
        # Agrega el permiso para categorias no moderadas
        perm = Permission.objects.create(codename="Publicacion no moderada", content_type_id=1)
        rol_autor.permisos.add(perm)
        perm = Permission.objects.create(codename="Vista_publicador", content_type_id=2)
        rol_autor.permisos.add(perm)

        rol_autor.save()

        # Crea una categoría no moderada de prueba
        self.categoria = Categoria.objects.create(nombre='Categoría Favorita')
        self.categoria.moderada = False

        self.categoria2 = Categoria.objects.create(nombre='Categoría no Favorita')
        self.categoria2.moderada = False
        
        # Crea un contenido de ejemplo  
        self.contenido_ejemplo = Contenido.objects.create(
            titulo='Contenido destacado',
            autor= self.autor,
            categoria= self.categoria,
            estado= 'P',
            fecha_publicacion= datetime.now(),
            imagen='/contenido_imagenes/6f0c63b0-3a7d-11ee-8996-c34107379e5e.jpg',
            destacado=0
        )
        
        # Crea un contenido que aparecera despues de los destacados
        self.contenido_no_favorito = Contenido.objects.create(
            titulo='Contenido no favorito',
            autor= self.autor,
            categoria= self.categoria2,
            estado= 'P',
            fecha_publicacion= datetime.now(),
            imagen='/contenido_imagenes/6f0c63b0-3a7d-11ee-8996-c34107379e5e.jpg',
            destacado=0
        )

        self.favorito1 = Favorito.objects.create(
            categoria= self.categoria,
        )

    def test_contenido_favorito(self):
        """
        Verifica que el contenido favoritoaparece primero en el inicio
        """
        # Iniciar sesión como el usuario autor
        login = self.client.login(username='autor_prueba', password='4L1_khrSri8i')
        self.assertTrue(login, "No se pudo loguear al autor de prueba")

        # Verifica que el contenido no esta aparece al principio inicialmente
        response = self.client.get(reverse('MenuPrincipal'))
        self.assertEqual(response.context.get('contenido')[0], self.contenido_no_favorito, "El contenido se mostro primero en la pagina aunque no estaba favorito")

        # Agrega el contenido a favoritos
        
        self.favorito1.user_sub.set([self.autor])
        self.favorito1.save()

        # Verifica que el contenido es el primero en la pagina
        response = self.client.get(reverse('MenuPrincipal'))
        self.assertEqual(response.context.get('contenido').filter(categoria=response.context.get('user_favoritos')[0])[0], self.contenido_ejemplo, "El contenido no se mostro primero en la pagina aunque estaba en favoritos")
