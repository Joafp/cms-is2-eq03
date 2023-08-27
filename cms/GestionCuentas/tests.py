from django.test import TestCase
from .models import Rol, UsuarioRol
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
