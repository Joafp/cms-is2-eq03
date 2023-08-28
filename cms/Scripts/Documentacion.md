<datils>
<sumary>Crear Script "crear_admin.py"</sumary>
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