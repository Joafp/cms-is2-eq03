from django.urls import path,include
from . import views
urlpatterns = [
    path('crear/',views.crear_categoria,name='Categoria'),
]
