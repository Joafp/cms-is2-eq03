from django import forms
from .models import Contenido
#Documentacion
class RazonRechazoForm(forms.ModelForm):
    class Meta:
        model = Contenido
        fields = ['razon_rechazo']