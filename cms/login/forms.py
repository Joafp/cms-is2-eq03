from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroForm(UserCreationForm):
    """
    Personalizamos el formulario de registro que nos proporciona django, agregando los campos de email, telefono
    NOmbres y apellidos. Tambien con attrs={'placeholder'} agregamos un texto de fondo para los campos de texto
    """
    email = forms.EmailField(widget= forms.EmailInput(attrs={'placeholder':'Ingrese su email'}) )
    telefono= forms.CharField(max_length=15,widget= forms.TextInput(attrs={'placeholder':'Ingrese su numero de telefono'}) )
    username=forms.CharField(min_length=8,max_length=15,widget= forms.TextInput(attrs={'placeholder':'Minimo 8 caracteres maximo 15'}) )
    password1=forms.CharField(min_length=8,max_length=15,widget= forms.TextInput(attrs={'placeholder':'Minimo 8 caracteres maximo 15'}))
    password2=forms.CharField(min_length=8,max_length=15,widget= forms.TextInput(attrs={'placeholder':'Minimo 8 caracteres maximo 15'}))
    nombres=forms.CharField(min_length=8,max_length=15,widget= forms.TextInput(attrs={'placeholder':'Minimo 8 caracteres maximo 15'}) )
    apellidos=forms.CharField(min_length=8,max_length=15,widget= forms.TextInput(attrs={'placeholder':'Minimo 8 caracteres maximo 15'}) )
    class Meta:
        model = User
        fields = ['username','nombres','apellidos', 'email','telefono', 'password1', 'password2']