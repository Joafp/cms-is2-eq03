from django.test import TestCase
from login.forms import RegistroForm
from django.urls import reverse
from login.views import registro, vista_login, cerrar_sesion
from GestionCuentas.models import Rol, UsuarioRol, PermisosPer
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

# Test de las etiquetas mostradas en el formulario de registro
class registroFormTest(TestCase):
    
    def test_registro_usuario_label(self):
        form = RegistroForm()
        self.assertTrue(form.fields['username'].label is None or form.fields['username'].label == 'username')

    def test_registro_nombres_label(self):
        form = RegistroForm()
        self.assertTrue(form.fields['nombres'].label is None or form.fields['nombres'].label == 'nombres')

    def test_registro_apellidos_label(self):
        form = RegistroForm()
        self.assertTrue(form.fields['apellidos'].label is None or form.fields['apellidos'].label == 'apellidos')

    def test_registro_email_label(self):
        form = RegistroForm()
        self.assertTrue(form.fields['email'].label is None or form.fields['email'].label == 'email')

    def test_registro_telefono_label(self):
        form = RegistroForm()
        self.assertTrue(form.fields['telefono'].label is None or form.fields['telefono'].label == 'telefono')

    def test_registro_password1_label(self):
        form = RegistroForm()
        self.assertTrue(form.fields['password1'].label is None or form.fields['password1'].label == 'password1')

    def test_registro_password2_label(self):
        form = RegistroForm()
        self.assertTrue(form.fields['password2'].label is None or form.fields['password2'].label == 'password2')


# Test de view registro
class registroViewTest(TestCase):
    
    def test_registro_url_existe(self):
        response = self.client.get('/login/registro/')
        self.assertEqual(response.status_code, 200)

    def test_registro_accesible_por_nombre(self):
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)

    def test_registro_usa_template_correcto(self):
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/registro.html')

# Test de view login
class loginViewTest(TestCase):
    
    def test_login_url_existe(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_accesible_por_nombre(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_usa_template_correcto(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

# Prueba de completar formulario de registro y de login
class completarRegistroLoginTest(TestCase): 
    # Crea usuarios, roles y permisos para el test
    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser123', password='4L1_khrSri8i')
        test_user1.save()

        test_user2 = User.objects.create_user(username='stafftestuser123', password='4L1_khrSri8i')
        test_user2.save()

        test_user1_rol=UsuarioRol.objects.create(
                username="testuser123",
                email="testuser123@test.com",
                nombres="test name", 
                apellidos="test lastname",
            )
        
        test_user2_rol=UsuarioRol.objects.create(
                username="stafftestuser123",
                email="stafftestuser123@test.com",
                nombres="test name", 
                apellidos="test lastname",
            )
        
        # setup permisos
    
        permisos = [
            Permission.objects.get(codename="Vista autor"),
            Permission.objects.get(codename="Vista editor"),
            Permission.objects.get(codename="Vista publicador"),
            Permission.objects.get(codename="Vista administrador")
        ]
        
        rol_suscriptor=Rol.objects.create(nombre='Suscriptor')
        rol_autor=Rol.objects.create(nombre='Autor')
        rol_editor=Rol.objects.create(nombre='Editor')
        rol_publicador=Rol.objects.create(nombre='Publicador')
        rol_administrador=Rol.objects.create(nombre='Administrador')

        rol_autor.permisos.add(permisos[0])
        rol_editor.permisos.add(permisos[1])
        rol_publicador.permisos.add(permisos[2])
        rol_administrador.permisos.add(permisos[3])

        rol_suscriptor.save()
        rol_autor.save()
        rol_editor.save()
        rol_publicador.save()
        rol_administrador.save()

        test_user1_rol.roles.add(rol_suscriptor)
        test_user1_rol.save()

        test_user2_rol.roles.add(rol_suscriptor, rol_autor, rol_administrador, rol_editor, rol_publicador)
        test_user2_rol.save()

    def test_registro_completo_redirige_a_login(self):
        email = "testuser@test.com"
        telefono = "000"
        username = "testuser123x"
        password1 = "4L1_khrSri8i"
        password2 = "4L1_khrSri8i"
        nombres = "test name"
        apellidos = "test lastname"
        response = self.client.post(reverse('registro'), {'email':email, 'telefono': telefono, 'username': username, 'password1': password1, 'password2': password2, 'nombres':nombres, 'apellidos': apellidos})
        self.assertRedirects(response, reverse('registro'))

    def test_login_redirige_a_pagina_principal(self):
        response = self.client.post(reverse('login'), {'username':'testuser123', 'password':'4L1_khrSri8i'})
        self.assertRedirects(response, reverse('MenuPrincipal'))

    def test_suscriptor_no_ve_botones_de_desarrollador(self):
        login = self.client.login(username='testuser123', password='4L1_khrSri8i')
        usuario_rol = UsuarioRol.objects.get(username='testuser123')
        response = self.client.get(reverse('maintrabajador'), {'usuario_rol': usuario_rol})
        self.assertInHTML('<button>Entrar como Autor</button>', response.content.decode(), 0)
        self.assertInHTML('<button>Entrar como editor</button>', response.content.decode(), 0)
        self.assertInHTML('<button>Entrar como publicador</button>', response.content.decode(), 0)
        self.assertInHTML('<button>Entrar como administrador</button>', response.content.decode(), 0)
        
    def test_administrador_ve_botones_de_desarrollador(self):
        login = self.client.login(username='stafftestuser123', password='4L1_khrSri8i')
        usuario_rol = UsuarioRol.objects.get(username='stafftestuser123')
        response = self.client.get(reverse('maintrabajador'), {'usuario_rol': usuario_rol})
        self.assertInHTML('<button>Entrar como Autor</button>', response.content.decode())
        self.assertInHTML('<button>Entrar como editor</button>', response.content.decode())
        self.assertInHTML('<button>Entrar como publicador</button>', response.content.decode())
        self.assertInHTML('<button>Entrar como administrador</button>', response.content.decode())
