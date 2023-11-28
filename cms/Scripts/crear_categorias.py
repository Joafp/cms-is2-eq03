# Importa el modelo Categoria
import os
import django
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
django.setup()
from core.models import Categoria  # Asegúrate de reemplazar 'tu_aplicacion' con el nombre real de tu aplicación.

def crear_categorias():
    # Crea cinco categorías
    categorias = [
        {"nombre": "Fútbol", "moderada": False, "activo": True},
        {"nombre": "Música", "moderada": True, "activo": True},
        {"nombre": "Cine", "moderada": True, "activo": True},
        {"nombre": "Tecnología", "moderada": True, "activo": True},
        {"nombre": "Viajes", "moderada": True, "activo": True},
    ]

    for categoria_data in categorias:
        Categoria.objects.create(**categoria_data)
        print(f"Categoría '{categoria_data['nombre']}' creada")

if __name__ == "__main__":
    crear_categorias()
