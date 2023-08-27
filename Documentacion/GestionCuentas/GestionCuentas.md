# Gestión de Cuentas

La aplicación de **Gestión de Cuentas** es responsable de administrar los roles, usuarios y permisos en nuestro sistema. Además, se encarga de definir los modelos fundamentales que son utilizados en otras aplicaciones del sistema.

## Funcionalidades Principales

1. **Roles y Permisos**: La aplicación permite definir y gestionar diferentes roles de usuarios, cada uno con sus respectivos permisos. Esto garantiza un control granular sobre las acciones que los usuarios pueden realizar en el sistema.

2. **Usuarios**: Proporciona las herramientas para crear, editar y eliminar cuentas de usuario. Los usuarios pueden ser asignados a roles específicos, lo que determina su acceso y funcionalidades disponibles.

3. **Modelos Fundamentales**: La Gestión de Cuentas es responsable de la creación y definición de los modelos esenciales que son compartidos y utilizados por otras partes del sistema. Estos modelos pueden incluir, por ejemplo, datos de perfil de usuario, información de autenticación, etc.

# Gestión de Cuentas

La aplicación de **Gestión de Cuentas** es responsable de administrar los roles, usuarios y permisos en nuestro sistema. Además, se encarga de definir los modelos fundamentales que son utilizados en otras aplicaciones del sistema.

## Librerías Utilizadas

Para implementar la funcionalidad de la Gestión de Cuentas, hemos utilizado las siguientes librerías de Django:
python
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission, User

## Clases

1. **UsuarioRol**: Esta clase se encarga de conectar la base de datos que viene por defecto en django y traer de la misma los usuarios registrados, luego de esto asigna un rol a dicho usuario

2. **Rol**: Esta clase fue hecha para poder editar los roles de nuestro sistema, darles nombres y agregar nuevo permisos a los mismos

3. **PermisosPer**: Nos permite crear nuevos permisos y darles una descripcion estos mismos se puede asociar luego con la clase Rol