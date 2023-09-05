from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,date
from ckeditor.fields import RichTextField
from GestionCuentas.models import UsuarioRol
from django.urls import reverse
class Contenido(models.Model):
    titulo= models.CharField(max_length=255)
    autor= models.ForeignKey(UsuarioRol,on_delete=models.CASCADE,limit_choices_to={'roles__nombre':'Autor'})
    cuerpo=RichTextField(blank=True,null=True)
    def __str__(self):
        return self.titulo+ '|'+ str(self.autor)
    def get_absolute_url(self):
        return reverse('crear_contenido')
    
class Categoria(models.Model):
    nombre=models.CharField(max_length=200)
    moderada=models.BooleanField(default=False)
    activo=models.BooleanField(default=True)

    def __str__(self):
        return self.name


