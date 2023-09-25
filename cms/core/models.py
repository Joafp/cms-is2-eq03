from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,date
from ckeditor.fields import RichTextField
from GestionCuentas.models import UsuarioRol
from django.urls import reverse

class Categoria(models.Model):
    nombre=models.CharField(max_length=200)
    moderada=models.BooleanField(default=False)
    activo=models.BooleanField(default=True)
    def __str__(self):
        return self.nombre
    
class Contenido(models.Model):
    ESTADOS = (
        ('B', 'Borrador'),
        ('E', 'En Edicion'),
        ('R', 'En Revisión'),
        ('P', 'Publicado'),
        ('r','Rechazado'),
        ('I','Inactivo'),
    )
    estado = models.CharField(max_length=1, choices=ESTADOS, default='B')
    titulo= models.CharField(max_length=255)
    autor= models.ForeignKey(UsuarioRol,on_delete=models.CASCADE,limit_choices_to={'roles__nombre':'Autor'})
    categoria= models.ForeignKey(Categoria,on_delete=models.CASCADE)
    resumen=models.CharField(max_length=255,blank=True)
    imagen = models.ImageField(upload_to='contenido_imagenes/', blank=True, null=True)
    cuerpo=RichTextField(blank=True,null=True)
    def __str__(self):
        return self.titulo+ '|'+ str(self.autor)
    def get_absolute_url(self):
        return reverse('crear_contenido')

