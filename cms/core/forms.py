from django import forms
from .models import Contenido

class RazonRechazoForm(forms.ModelForm):
    class Meta:
        model = Contenido
        fields = ['razon_rechazo']