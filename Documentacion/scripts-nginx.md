# Documentacion de los scripts para configurar nginx


## Instalacion y Configuracion
Para configurar los servidores en el entorno de produccion se crearon dos Scripts
Antes de ejecutarlos es necesario instalar el app server gunicorn en **el entorno virtual en el que se instalo el framework django**:


```python
pip install gunicorn
```


Y tambien hay que instalar el webserver nginx

```bash
sudo apt install nginx
```

Una vez instalados hay que editar los scripts para establecer algunas variables:

**setup_GUNI.sh**

```bash
username=<nombre de usuario del host>
carpetaproyecto=<direccion a la carpeta donde se encuentra manage.py>
gunicorn=<direccion absoluta al archivo "gunicorn" que se encuentra en la carpeta bin/ del entorno virtual>
```

**setup_NGINX.sh**
```bash
carpetaproyecto=<direccion a la carpeta donde se encuentra manage.py>
serverIP=<direccion IP o nombre del servidor>
```

Finalmente se ejecutan los archivos:
```bash
sudo ./setup_GUNI.sh
sudo ./setup_NGINX.sh
```

Y esto permite acceder al sitio web desde la direccion establecida

## Explicacion de los scripts

**setup_GUNI.sh**

Este script crea dos archivos
1. **/etc/systemd/system/gunicorn.socket**, que crea un socket para escuchar las peticiones
2. **/etc/systemd/system/gunicorn.service**, que crea un servicio en segundo plano para servir la aplicacion al recibir una peticion. Este servicio tambien se ejecutara al reiniciar el pc

**setup_NGINX.sh**

Este script crea un archivo:
1. **/etc/nginx/sites-available/cmsis2e03**, que escucha las conexiones a la IP en el puerto 8080, sirve los archivos estaticos y redirecciona las peticiones al gunicorn.
2. Luego copia el archivo a **/etc/nginx/sites-enabled** y reinicia el servidor de nginx para que se registren los cambios
