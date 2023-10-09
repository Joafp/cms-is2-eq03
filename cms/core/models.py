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
    """
    El modelo contenido nos sirve para guardar los datos del contenido, tenemos los atributos
    Titulo: guardamos el titulo del contenido
    Autor: Asignamos un autor al titulo, mediante el codigo podemos ver que usamos limit choices para buscar solo los usuarios con el rol
    autor
    Categoria: En nuestro caso usamos el modelo creado anteriormente llamado categoria, como vemos asignamos que 
    un contenido solo puede pertenecer a una categoria
    Imagen: utilizamos el modelo default de django que nos ofrece ImageField, en este atributo lo que guardamos es el path
    de la imagen, en upload asingamos la ubicacion donde se guardara la imagen
    Cuerpo: Utilizamos la libreria ckeditor, esta libreria nos permite crear field enriquesidos, donde podemos subir tanto imagenes, como textos
    """
    ESTADOS = (
        ('B', 'Borrador'),
        ('E', 'En Edicion'),
        ('R', 'En Revisión'),
        ('P', 'Publicado'),
        ('r','Rechazado'),
        ('I','Inactivo'),
    )
    estado = models.CharField(max_length=1, choices=ESTADOS, default='B')
    titulo= RichTextField(blank=True,null=True,config_name='limite_caracteres')
    autor= models.ForeignKey(UsuarioRol,on_delete=models.CASCADE,limit_choices_to={'roles__nombre':'Autor'},related_name='contenidos_autor',null=True)
    editor = models.ForeignKey(UsuarioRol, on_delete=models.CASCADE, limit_choices_to={'roles__nombre': 'Editor'}, related_name='contenidos_editor',null=True)
    publicador = models.ForeignKey(UsuarioRol, on_delete=models.CASCADE, limit_choices_to={'roles__nombre': 'Publicador'}, related_name='contenidos_publicador',null=True)
    categoria= models.ForeignKey(Categoria,on_delete=models.CASCADE)
    resumen=RichTextField(blank=True,null=True,config_name='limite_caracteres')
    imagen = models.ImageField(upload_to='contenido_imagenes/', blank=True, null=True)
    cuerpo=RichTextField(blank=True,null=True)
    razon = RichTextField(blank=True,null=True,config_name='limite_caracteres')
    ultimo_editor=models.CharField(max_length=255,blank=True)
    ultimo_publicador=models.CharField(max_length=255,blank=True)
    fecha_publicacion = models.DateField(null=True, blank=True)
    me_gusta = models.PositiveIntegerField(default=0)
    no_me_gusta = models.PositiveIntegerField(default=0)
    compartido = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.titulo+ '|'+ str(self.autor)
    """Nos permite una vez creado el contenido redireccionar a la misma pagina para pooder seguir creando contenidos
    en caso de querer redireccionar a otr pagina solo cambiamos reverse()"""
    def get_absolute_url(self):
        return reverse('crear_contenido')

class HistorialContenido(models.Model):
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE)
    cambio = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cambio en {self.contenido.titulo} - {self.fecha}"