from django.test import TestCase
from django.urls import reverse
from .models import Contenido, Categoria
from GestionCuentas.models import UsuarioRol, Rol
from django.contrib.auth.models import Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from ckeditor.fields import RichTextField
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
        self.categoria = Categoria.objects.create(nombre='Categoría de Prueba')
        self.contenido = Contenido.objects.create(
            titulo='Título de Prueba',
            autor=self.autor,
            categoria=self.categoria,
            resumen='Resumen de prueba',
            cuerpo='Cuerpo de prueba',
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
    def tearDown(self):
        # Limpieza de datos de prueba si es necesario
        self.autor.delete()
        self.categoria.delete()
