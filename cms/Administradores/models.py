from django.db import models
class admnistradores (models.Model):
    nombre=models.CharField(max_length=50)
    password=models.CharField(max_length=30)
    def __str__(self):
        return self.nombre
