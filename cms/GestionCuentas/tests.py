from django.test import TestCase
from .models import Rol, UsuarioRol
class RolCrearTestCase(TestCase):
    def setUp(self):
        self.crear()
    def crear(self):
       Rol.objects.create(nombre='Prueba')
    def test_nombre(self): 
        item=Rol.objects.get(nombre='Prueba')
        self.assertEqual(item.nombre,"Prueba")
