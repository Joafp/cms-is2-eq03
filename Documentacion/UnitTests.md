# Unit Tests
Para  comprobar el funcionamiento correcto de las aplicaciones se utiliza el descubrimiento de test automatico proveido por django.
Cada aplicacion contiene un archivo *tests.py* con los test correspondientes a esa aplicacion.
Los archivos de test tienen la siguiente estructura:

```python
from django.test import TestCase

class loginTest(TestCase):
    def setUp(self):
        ...

    def setUpTestData(cls):
        ...

    def testCase(self):
        ...
```

- El import ```from django.test import TestCase``` permite heredar de la clase TestCase para definir los Test
- Las funciones ```setUp()``` y ```setUpTestData()``` permiten crear datos de prueba en la base de datos creada por el test
- Las demas funciones como ``` testCase()``` son ejecutadas durante el test y contienen aserciones que se prueban para encontrar errores

## Ejecucion

Para ejecutar los test se utiliza el comando:
```python manage.py test```

Que ejecuta todos los test cuyo nombre de archivo siga la forma tests*.py

## Aplicaciones con Test

- [login](../cms/login/tests.py)
- [GestionCuentas](../cms/GestionCuentas/tests.py)


