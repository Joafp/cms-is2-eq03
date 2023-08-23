from django.test import TestCase
from .models import Rol, UsuarioRol
class RolTestCase(TestCase):
    def crear(self):
        Rol.objects.create(name="Rol_Prueba")
    def test_nombre(self):
        item=Rol.objects.get(name="Rol_Prueba")
        self.assertEqual(item.nombre,"Rol_Prueba")

