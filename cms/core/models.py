from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,date
from ckeditor.fields import RichTextField
from GestionCuentas.models import UsuarioRol
from django.conf import settings
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
    destacado= models.PositiveIntegerField(default=0)
    veces_visto= models.PositiveIntegerField(default=0)
    veces_compartido = models.PositiveIntegerField(default=0)
    stars = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='B')
    titulo= RichTextField(blank=True,null=True,config_name='limite_caracteres')
    titulo_abreviado=RichTextField(blank=True,null=True,config_name='limite_caracteres')
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
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    promedio_calificaciones = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    def __str__(self):
        return self.titulo+ '|'+ str(self.autor)
    """Nos permite una vez creado el contenido redireccionar a la misma pagina para pooder seguir creando contenidos
    en caso de querer redireccionar a otr pagina solo cambiamos reverse()"""
    def get_absolute_url(self):
        return reverse('crear_contenido')
    
    @property
    def contenido_programado(self):
        # Retorna true si el contenido esta programado para publicarse en una fecha posterior
        return self.fecha_publicacion > datetime.now()
    
    @property
    def moderado(self):
        # Retorna true si el contenido esta en una categoria moderada
        return self.categoria.moderada

    


class Calificacion(models.Model):
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return f'Calificación de {self.usuario.username} en {self.contenido.titulo}'    

class HistorialContenido(models.Model):
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE)
    cambio = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cambio en {self.contenido.titulo} - {self.fecha}"
    
class VersionesContenido(models.Model):
    """
    Guarda una copia de los campos de un contenido. Tambien guarda el numero de version y la fecha en que se guardo la copia.
    Contiene una referencia al contenido al que pertenece la version para facilitar la restauracion de una version.
    """
    contenido_base = models.ForeignKey(Contenido, on_delete=models.CASCADE)
    numero_version = models.PositiveIntegerField()
    fecha_version = models.DateTimeField(auto_now_add=True)

    titulo= RichTextField(blank=True,null=True,config_name='limite_caracteres')
    categoria= models.ForeignKey(Categoria,on_delete=models.CASCADE)
    resumen=RichTextField(blank=True,null=True,config_name='limite_caracteres')
    imagen = models.ImageField(upload_to='contenido_imagenes/', blank=True, null=True)
    cuerpo=RichTextField(blank=True,null=True)
    razon = RichTextField(blank=True,null=True,config_name='limite_caracteres')
    def __str__(self):
        return self.fecha_version + '| v' + self.numero_version + '|' + self.razon


class Comentario(models.Model):
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f'Comentario de {self.autor} en {self.contenido.titulo}'
    
class Likes(models.Model):
    """
    Guarda que usuarios indicaron like/dislike en un contenido
    """
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE, related_name='contenido')
    user_likes = models.ManyToManyField(UsuarioRol, related_name='likes')
    user_dislikes = models.ManyToManyField(UsuarioRol, related_name='dislikes')

    def str(self):
        return f'Numero de likes:dislikes en {self.contenido.titulo}: {self.user_likes_count}:{self.user_dislikes_count}'
    
    def user_likes_count(self):
        return self.user_likes.all().count()

    def user_dislikes_count(self):
        return self.user_dislikes.all().count()
    
class Favorito(models.Model):
    """
    Guarda que usuarios indicaron como favorito una categoria
    """
    categoria= models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='categoria')
    user_sub = models.ManyToManyField(UsuarioRol, related_name='user_sub')

    def str(self):
        return f'Numero de sub:en {self.categoria.nombre}: {self.user_subs_count}'
    
    def user_subs_count(self):
        return self.user_sub.all().count()

class Reporte(models.Model):
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE)
    usuario = models.ForeignKey(UsuarioRol, on_delete=models.CASCADE)
    texto = models.TextField(verbose_name="Razon de reporte")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
