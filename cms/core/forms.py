from django import forms
from django.forms import CharField
from django.core.exceptions import ValidationError
from .models import Contenido
from GestionCuentas.models import UsuarioRol
#Documentacion
class RazonRechazoForm(forms.ModelForm):
    class Meta:
        model = Contenido
        fields = ['razon']


class CrearContenidoForm(forms.ModelForm):
    class Meta:
        model= Contenido
        fields = ['titulo', 'autor', 'categoria', 'resumen', 'imagen', 'cuerpo', 'razon']
        widgets = {'autor': forms.HiddenInput()}
    

    def clean_imagen(self):
       data = self.cleaned_data.get("imagen")
       if not data:
            raise ValidationError("La imagen no puede estar vacia")
       return data
    
       
    def clean(self):
        cleaned_data = super().clean()
        autor = cleaned_data.get("autor")
        categoria = cleaned_data.get("categoria")

        if autor and categoria:
            if categoria.moderada == False:
                if autor.has_perm("Publicacion no moderada") == False:
                    raise ValidationError("Este autor no tiene permiso para publicar en categorias no moderadas")
        else:
            raise ValidationError("Falta el autor o la categoria")

        
