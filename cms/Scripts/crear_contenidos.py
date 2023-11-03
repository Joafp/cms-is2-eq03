import os
import django
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
django.setup()
from core.forms import CrearContenidoForm  # Asegúrate de importar el formulario correctamente.
from core.models import Contenido, UsuarioRol,Categoria
from django.core.files import File

def crear_contenido_borrador(categoria_nombre, autor_username):
    try:
        categoria = Categoria.objects.get(nombre=categoria_nombre)
        autor = UsuarioRol.objects.get(username=autor_username)
        contenido = Contenido.objects.create(
            titulo=f"Título de Prueba de {categoria_nombre}",
            autor=autor,
            categoria=categoria,
            resumen=f"Resumen de prueba de {categoria_nombre}",
            cuerpo=f"Cuerpo de prueba de {categoria_nombre}",
            imagen="contenido_imagenes/ASUNCIÓN_Asunción_Paraguay_3ojm1wQ.jpg"
        )
        contenido.save()

    except Categoria.DoesNotExist:
        print(f"Categoría '{categoria_nombre}' no encontrada.")
    except UsuarioRol.DoesNotExist:
        print(f"Usuario '{autor_username}' no encontrado.")

# Llama a la función para crear contenido en estado borrador para cada categoría
categorias_a_crear = ["Fútbol", "Música", "Cine", "Tecnología", "Viajes"]
autor_username = "Joadmin"
for categoria_nombre in categorias_a_crear:
    crear_contenido_borrador(categoria_nombre, autor_username)
