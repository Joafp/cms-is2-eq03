from django import forms
from .models import Rol
class RolForm(forms.ModelForm):
    class Meta:
        model=Rol
        fields=['nombre','descripcion']