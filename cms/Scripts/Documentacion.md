<datils>
<sumary>Crear Script "crear_admin.py"</sumary>
El orden en el cual deben de ejecutarse los scripts es el siguiente, primeramente se debe crear los roles en el sistema esto permitira asignar a cada ususario un rol, luego de esto ejecutar el script crear usuario, esto carga 4 usuarios que serian el administrador, el autor, el editor y un publicador, luedo de estro le damos a crear_admin para darle todos los permisos al administrador y para los contenidos primero ejecutamos el script crear categoria y luego crear contenidos
Para ejecutar los scripts se utiliza python crear_admin.py, tambien debemos de estar en la carpeta que contiene los scripts
script: crear_admin.py
Nos permite asingar el rol de administrador a un usuario que creemos en el sistema, mediante esto
podremos entrar en el /admin de django. Para poder ejecutar correctamente este script primeramente debemos de correr el servidor y crear un nuevo usuario, este tendra el rol de suscriptor por defecto y al correr el script modificara sus roles para tener el admin
        ```usuario=UsuarioRol.objects.get(username='JoaAdministrado')
        user=User.objects.get(username='JoaAdministrado')```
En username debemos de colocar el username de la persona que queremos asignar el rol de superusuario

Para ejecutar los scripts se utiliza python crear_roles.py, tambien debemos de estar en la carpeta que contiene los scripts
script: crear_roles.py
Este script nos permite crear roles por defecto en nuestro sistema, esto si no se quiere usar el /admin de django, por defecto pusimos que se creen los roles de autor, editor y publicador.  En caso de querer agregar mas roles se tiene que modificar 
    ```roles=[
        {"nombre":"Autor"},
        {"nombre":"Editor"},
        {"nombre":"Publicador"},
    ]```