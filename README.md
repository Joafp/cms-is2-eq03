# Proyecto-IS2-CMS-Grupo3
Para correr el programa es necesario tener instaladas las sigientes dependencias:

- Python3

  - Como instalar python en distribuciones basadas en Ubuntu.    [Mas info](https://docs.python-guide.org/starting/install3/linux/)
        


- Django:

  - Como instalar django en distriibuciones basadas en ubuntu.    [Mas info](https://pythondiario.com/2021/03/como-instalar-y-configurar-django-en-ubuntu-20-04.html)

- PostgreSql 14:

  - Como instalar Postgresql para distribuciones basadas en ubuntu.    [Mas info](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-20-04-es)

 - Dbeaver o pgadmin4
    
    - Como instalar Dbeaver para distribuciones basadas en ubuntu.    [Mas info](https://blonder413.wordpress.com/2021/05/20/instalar-dbeaver-ce-en-ubuntu-20-04/)
    - Como instalar pgadmin4 para distribuciones basadas en ubuntu.    [Mas info](https://noviello.it/es/como-instalar-pgadmin4-en-ubuntu-20-04-lts/)

- IDE(Visual Studio Code)    

  - Instalar Visual Studio Code para distribuciones basadas en ubuntu.    [Mas info](https://www.arsys.es/blog/como-instalar-visual-studio-code-en-ubuntu)

- Virtual env
   - Instalar virtalenv para distribuciones basadas en ubuntu.    [Mas info](https://ludwingperezt.medium.com/instalar-virtualenv-con-python3-en-ubuntu-20-04-11729720ec53)


# Ejecucion del programa en un entorno local

Primero activamos el entorno virtual,ingresando al directorio /env/bin y ejecutar el comando:

- source activate 


Para ejecutar el programa debemos entrar en eldirectorio cms(Proyecto) y ejecutar el comando: 
 
 - python3 manage.py runserver 

Copiar el link del localhost mostrado en un navegador.

# APPS

- cms    [Ver documentacion](Documentacion/cms.md)
- core    [Ver documentacion](Documentacion/core.md)
- login     [Ver documentacion](Documentacion/login/login.admin.html)
- GestionCuentas    [Ver documentacion](Documentacion/GestionCuentas.md)
- Scripts-Nginx y Guunicorn [Ver documentacion](Documentacion/scripts-nginx.md)
