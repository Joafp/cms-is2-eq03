from django.db import models
from django import forms
from django.contrib.auth.models import AbstractBaseUser

class Rol(models.Model):
    nombre=models.CharField(max_length=50,unique=True)
    descripcion=models.TextField()
    def __str__(self):
        return self.nombre
class RolForm(forms.ModelForm):
    class Meta:
        model=Rol
        fields=['nombre','descripcion']
    


