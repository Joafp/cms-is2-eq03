from django.test import TestCase
from login.forms import RegistroForm
from django.urls import reverse
from login.views import registro, vista_login, cerrar_sesion
from GestionCuentas.models import Rol, UsuarioRol
from django.contrib.auth.models import User

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
        response = self.client.get('/registro/')
        self.assertEqual(response.status_code, 200)

    def test_registro_accesible_por_nombre(self):
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)

    def test_registro_usa_template_correcto(self):
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/registro.html')

# Prueba de registro y login
class registroCompletadoTest(TestCase): 
    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser123', password='4L1_khrSri8i')
        test_user1.save()

        rol_suscriptor=Rol.objects.create(nombre='Suscriptor')
        rol_suscriptor.save()

        test_user1_rol=UsuarioRol.objects.create(
                username="testuser123",
                email="testuser123@test.com",
                nombres="test name", 
                apellidos="test lastname",
            )

        test_user1_rol.roles.add(rol_suscriptor)
        test_user1_rol.save()

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

    # Falta: Probar acceso correcto del rol de desarrollador, Probar acceso no permitido a usuarios sin permisos, Probar que los botones no aparecen a suscriptores
