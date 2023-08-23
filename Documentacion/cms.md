# Documentacion del Proyecto Principal (cms)

- Modulo __init__.py nos indica que es un paquete.

- Modulo settings.py

  - Instalacion de apps
    ```
    INSTALLED_APPS = [
     'django.contrib.admin',
     'django.contrib.auth',
     'django.contrib.contenttypes',
     'django.contrib.sessions',
     'django.contrib.messages',
     'django.contrib.staticfiles',
      #App login
     'login.apps.LoginConfig',
     'Administradores', 
      #App core
     'core.apps.CoreConfig',
    ]
    ```
     Esta parte del codigo se encarga de importar todas las caracteristicas de nestras apps creadas como el login, donde cargamos con el comando 'login.apps.LoginConfig' todas las configuraciones de esta app para poder migrar y que la app se integre en el proyecto.Por otro lado tenemos algunas definidas por default de django como el contrib.auth para autenticar inicio de sesion o contrib.admin. 

   - Conexion con la base de datos  
      ```
      DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql_psycopg2',
             'NAME': 'usuarios_cms',
             'USER': 'equipo3_admin',
             'PASSWORD': '1234',
             'HOST': 'localhost',
             'PORT': '5432',
           }
        }
      ``````
      En esta parte del codigo especificamos las caraceristicas de la conexion a la base de datos que usaremos en el entorno de desarrollo. En ENGINE definimos que usareos el postgresql con la libreria psycopg2. El owner de la database sera equipo3_admin y la database tendra el nombre de usuarios_cms. Usamos el localhost ya que nuestro entorno de desarrollo esta enfocado en lo local, para esto ocupamos el puerto default 5432.

    - Redirecciones
       
       ```
       LOGIN_REDIRECT_URL= '/home'
       LOGIN_REDIRECT_URL= '/login'
       ´´´
       
       Estas asignaciones la hacemos para que al logearte nos tire al directorio /home que es la direccion de nuestro menu principal

    - Manejo de archivos estaticos
      ```
      STATIC_URL = 'static/
      ```
      Esta ruta la creamos para que el sistema encentre los archivos que contienen imagenes, o estilos. 

- urls.py
    ```
    from django.contrib import admin
    from django.urls import path, include
    from django.contrib.auth import urls

    urlpatterns = [
       path('', include('login.urls')),
       path('accounts/', include('django.contrib.auth.urls')),
       path('', include('core.urls')),
       path('admin/', admin.site.urls),
    ]
    ```

    Importamos de django.url path e include , para poder crear directorios navagebles en la pagina, el path para direccionar e inclde para poder incluir librerias o modulos de otros paquetes.
    
    La linea : path('accounts/', include('django.contrib.auth.urls')) , nos permite autenticar los usuarios a la hora de logearnos en el sitio
    Luego incluimos las urls de login y core. Por ultimo tenemos el admin/ que nos permite entrar en modo administrador, con una interfaz puesta por django, para poder administrar la pagina desde un entorno visual.