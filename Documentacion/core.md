# Documentacion de la app core

Para tener una idea, esta app llamada core es el nucleo de neustro programa, donde tenemos las vistas principales del sistema entre otras cosas. A continuacion se describiran los modulos que hacen funcionar esta app.

# Modulos
- apps.py
  
   Este modulo se utiliza para configurar la aplicacion definida.

   ```
   from django.apps import AppConfig
   class CoreConfig(AppConfig):
     default_auto_field = 'django.db.models.BigAutoField'
     name = 'core'
   ```

   La clase AppConfig esuna clase base que se utiliza para configurar la aplicacion django y personalizar su comportamiento en caso de ser necesario.
   Luego tenemos la clase CoreConfig(AppConfig),donde heredamos de AppConfig y utilizamos el CreCOnfig para la configuracion de nuestra app.
   En la linea 'default_auto_field' Cnfiguramos el tipo de campo automatico que utilizara para las claves primarias de los modelos en esta aplicacion.
   Por Ultimo le damos el nombre de 'core' a nuestra aplicacion. 
   Todo esto lo genera Automatico el django con el comando : 'python manage.py startapp core', ejecutando en el directorio donde se encuentra el manage.py.

- urls.py
   Este modulo se utiliza para definir como las distintas vista de tu aplicacion se relacionan con las direcciones de nuestro sitio.
   
   ```
   from django.urls import path
   from . import views
   urlpatterns = [
     path('menuprincipal/',views.vista_MenuPrincipal,name='MenuPrincipal')
    ]
   
   ```
   Primero importamos path del paquete urls de django, esto para poder definir las rutas URL en la aplicacion.
   Tambien importamos las views de nuestra aplicacion, donde se encuentran las distintas vistas creadas. En este caso necesitamos la 'vista_MenuPrincipal' direccionar a un Menu principal creada en esa vista cuando vayamos al directorio '/menprincipal'.
   Por ultimo en 'name='MenuPrincipal'' proporcionamos un nombre unico en esta ruta, lo que nos sirve para hacer referencia a ella desde otras partes del codigo, como por ejemplo plantillas HTML.

- views.py
  
  En esta seccion estaremos creando las distintas vistas de que contiene nuestra aplicacion.

  ```
   from django.shortcuts import render, HttpResponse
   from django.contrib.auth.decorators import login_required

   @login_required(login_url="/login")
   def vista_MenuPrincipal(request):
      return render(request,'crear/main.html')
  
  ```
  Primero importamos render delpaqete shortcuts que nos proporciona django, que nos servira para responder un request con un template.
  Luego tambien importamos login_required que nos permitira mostrar la vista solamente si el usuario se encuentra logeado en el sitema.
  La linea '@login_required(login_url="/login")' describe esto. La vista creada 'vista_MenuPrincipal' solo podra ser accedida una vez el usuario haya iniciado sesion, esto tiene sentido ya que en la vista lo que hacemos es responder el request con el directorio 'crear/main.html' que es el template del menu principal.
  