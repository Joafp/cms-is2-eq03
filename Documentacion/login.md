# Documentacion de la app Login.

Esta app , haciendo una breve descripcion, nos sirve paraquue los usuarios puedan iniciar al sitio y dirigirse al Menu Principal o Registrarse en caso de que no tengan una cuenta.

# Modulos y templates

- templates
   
   En esta carpeta estaremos almacenando los archivos HTML que seran utilizados para el inicio de sesion, registro y menu principal.
   
   Dentro de la carpeta templates tenemos

   - Crear
      
      Tenemos los archivos: 
        
        - main.html

            ```
            <!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Página de Contenidos</title>
            <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                }
            .header {
                background-color: #f2f2f2;
                padding: 10px;
                text-align: right;
                }
            .content {
                padding: 20px;
                }
            .admin-button {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                }
            </style>
            </head>
            <body>
            <div class="header">
                <button class="admin-button">Ingresar como administrador</button>
            </div>
            <div class="content">
                <!-- Aquí puedes agregar contenido dinámico -->
                <h1>Contenidos</h1>
                <p>Este es un ejemplo de página de contenidos.</p>
            </div>
            </body>
            </html>
           ```
            Como vemos es una estructura del menu principal, donde encontramos contenidos estaticos con mensajes,un estilo incorporado en el apartado de style donde, con css, le dimos forma a nuesto menu principal.
            Lo interesante a resaltar en este codigo seria el boton ingrear como administrador el cual nos permitira entrar en la vista del admin del sitio.

    
    - main

       Aqui se encuentra el template  registro.html que es la pagina donde se le manda al usuario cuando hace click en el boton Crear Usuario(mostrado mas adelante).
       
       ``` 
            <!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Registro</title>
            <style>
            body {
                background-color: #121212;
                color: #FFFFFF;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                width: 400px;
                padding: 40px;
                background-color: #1E1E1E;
                border-radius: 8px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3);
                text-align: center;
            }
            label {
                text-align: left;
                display: block;
                margin-bottom: 5px;
            }
            input {
                width: 100%;
                padding: 10px;
                margin-bottom: 10px;
                border: 1px solid #333;
                border-radius: 4px;
                background-color: #282828;
                color: #FFFFFF;
            }
            button {
                margin: 0 auto;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                background-color: #1976D2;
                color: #FFFFFF;
                cursor: pointer;
            }
            .forgot-password {
                text-align: center;
                margin-top: 20px;
            }
            .create-account {
                text-align: right;
                margin-top: 10px;
            }
            body{
                display:flex;
                flex-direction: column;
            }
            .volver{
            display:flex;
            flex-direction: row;
            justify-content: space-around;
            }
           </style>
          </head>
          <body>
          <h1>Registro</h1>
          <form method="post">
          {% csrf_token %}
          {{ form.as_p }}
          <div class="volver">
          <button type="submit">Registrarse</button>
          <a href="{% url 'login' %}">Volver a iniciar sesión</a>
          </div>
          </form>
          <br>
          </body>
          </html>       
                
       ```

       Renderizamos un formulario llamado post,modificado para ajustar a nuestros requisitos, en la parte de forms.py de esta app(descrita mas adelante).
       La linea form method="post" nos indica que todo lo escrito se enviaran al servidor cuando el usuario haga clic en el boton "Guardar"
       El '{{form.as_p}}' renderiza los campos del formulario utilizando el formato de parrafo para cada campo.
       Tambien agregamos aparte del formulario un boton para guardar los datos. 
       Tambien el la parte del boton volver se agrego un href para dirigir al login una vez creada la cuenta.
       El boton Registrarse se dirige a si mismo para que se reseteen los campos. Es decir una vez registrado el usuario debera dar al boton volver a iniciar sesion para logearse.
    
    - registration
       
       En esta carpeta se encuentra el template de inicio de sesion que se muestra en la pantalla principal del sistema 'login.html'.

       ```
            <!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Iniciar sesión</title>
            <style>
            body {
                background-color: #121212;
                color: #FFFFFF;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                width: 400px;
                padding: 40px;
                background-color: #1E1E1E;
                border-radius: 8px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3);
                text-align: center;
            }
            label {
                display: block;
                text-align: center;
                margin-bottom: 10px;
            }
            input {
                width: 100%;
                padding: 10px;
                margin-bottom: 10px;
                border: 1px solid #333;
                border-radius: 4px;
                background-color: #282828;
                color: #FFFFFF;
            }
            button {
                display: block;
                margin: 0 auto;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                background-color: #1976D2;
                color: #FFFFFF;
                cursor: pointer;
            }
            .forgot-password {
                text-align: center;
                margin-top: 20px;
            }
            </style>
            </head>
            <body>
            <div class="container">
                <h2>Iniciar sesión</h2>
                <form method="post">
                    {% csrf_token %}
                    {{ form.as_p }}
                    <button type="submit">Acceder</button>
                    <br>
                    <a href="{% url 'registro' %}">Crear una cuenta</a>
                </form>
            </div>
            <br>
            <br>
            <div class="create-account">
                
            </div>
            </body>
            </html>
       ```
       En resumen , el formulario lo cargamos de la misma manera que hicimos con el menu de registro, {{ form.as_p }} para cargar el formulario , en diferencia al registro , no modificamos el original de django.
       Usamos tambien el mismo metodo

- app.py
    
    Este modulo se utiliza para configurar la aplicacion definida.

    ```
    from django.apps import AppConfig
    class LoginConfig(AppConfig):
        default_auto_field = 'django.db.models.BigAutoField'
        name = 'login'
    ```

    La clase AppConfig esuna clase base que se utiliza para configurar la aplicacion django y personalizar su comportamiento en caso de ser necesario.
    Luego tenemos la clase LoginConfig(AppConfig),donde heredamos de AppConfig y utilizamos el LoginConfig para la configuracion de nuestra app.
    En la linea 'default_auto_field' Cnfiguramos el tipo de campo automatico que utilizara para las claves primarias de los modelos en esta aplicacion.
    Por Ultimo le damos el nombre de 'login' a nuestra aplicacion. 
    Todo esto lo genera Automatico el django con el comando : 'python manage.py startapp login', ejecutando en el directorio donde se encuentra el manage.py.

- forms.py
    
    Este modulo creamos para modificar el formulario de registro por defecto de django, ya que este no traia los campos de email y numero de telefono.

    ```
        from django import forms
        from django.contrib.auth.forms import UserCreationForm
        from django.contrib.auth.models import User

        class RegistroForm(UserCreationForm):
            email = forms.EmailField(widget= forms.EmailInput(attrs={'placeholder':'Ingrese su email'}) )
            telefono= forms.CharField(max_length=15,widget= forms.TextInput(attrs={'placeholder':'Ingrese su numero de telefono'}) )
            username=forms.CharField(min_length=8,max_length=15,widget= forms.TextInput(attrs={'placeholder':'Minimo 8 caracteres maximo 15'}) )
            password1=forms.CharField(min_length=8,max_length=15,widget= forms.TextInput(attrs={'placeholder':'Minimo 8 caracteres maximo 15'}))
            password2=forms.CharField(min_length=8,max_length=15,widget= forms.TextInput(attrs={'placeholder':'Minimo 8 caracteres maximo 15'}))
            class Meta:
                model = User
                fields = ['username', 'email','telefono', 'password1', 'password2']
    
    ```

    Basicamente lo que hicimos fue heredar de la clase UserCreationForm para tener los campos default., luego agregamos el email y telefono.
    E cada campo le colocamos unu minimo y maximo de numero de caracteres como tambien un widget para mostrar un mensaje dentro del campo del cuaudro de texto.

- urls.py
    
    Este modulo se utiliza para definir como las distintas vista de tu aplicacion se relacionan con las direcciones de nuestro sitio.

    ```
    from django.urls import path
    from . import views
    from core import views as menu

    urlpatterns = [
    path('',views.vista_login,name='login'),  
    path('menuprincipal/',menu.vista_MenuPrincipal,name='MenuPrincipal'),
    path('registro/', views.registro, name='registro'),
    ] 

    ```

    En este caso tenemos la vista_login importada de views, que nos redireccionara a la vista de inicio de sesion. El menuprincipal/ que nos direccionara al template del Menu Principal.
    Por ultimo el /registro que nos direccionara a la pagina de registro.

- views.py

    En este modulo definimos las vistas del inicio de sesion y registro de la siguiente manera :

    ```
        from django.contrib.auth.forms import AuthenticationForm
        from django.contrib.auth import authenticate, login
        from django.shortcuts import render,redirect
        from django.views.decorators.cache import never_cache
        from .forms import RegistroForm
        @never_cache
        def vista_login(request):
        if request.method == 'POST':
            form = AuthenticationForm(request, request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    print("Usuario autenticado. Redireccionando...")
                    return redirect('MenuPrincipal')  # Redireccionar al menú principal
                else:
                    print("Usuario no autenticado.")
            else:
                print("Formulario no válido.")
        else:
            form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})

        @never_cache
        def registro(request):
            if request.method == 'POST':
                form = RegistroForm(request.POST)
                if form.is_valid():
                    form.save()
                    return redirect('registro')  # Redirigir a la página de inicio de sesión
            else:
                form = RegistroForm()
            return render(request, 'main/registro.html', {'form': form})
            
    ```

    Explicando primero la vista_login, recibe un request , y si es un post entonces autenticamos el form con la funcion AuthenticationForm importada de la libreria ath.forms , esto lo que hace es ver si el formulario cuumple con los campos, es decir , numero de caracteres entre otras cosas.
    Ua vez si es valido recuperamos el username y el password y usamos la libreria authenticate ,importada de contrib.auth, para ver si el usuario existe en nuestro sistema, de existir se le redireccionara al Menu principal y se logeara en el sistema, en caso contrario se mostrara un mensaje de usuario no autenticcado.



    En caso del registro, funciona de manera un poco similar a lo descrito anteriormente, solo que una vez que el form sea valido, enves de auntenticas guardamos en nuestra base de datos la informacion.

    El @never_cache lo utilizamos para borrar el cache del navegador.

    


       
