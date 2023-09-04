from django.db import models

from django.db import models
class Categoria(models.Model):
    nombre=models.CharField(max_length=200)
    moderada=models.BooleanField(default=False)
    activo=models.BooleanField(default=True)

    def __str__(self):
        return self.name


