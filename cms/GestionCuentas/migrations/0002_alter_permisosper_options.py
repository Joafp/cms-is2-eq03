# Generated by Django 4.2.4 on 2023-10-29 19:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GestionCuentas', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='permisosper',
            options={'permissions': [('Boton desarrollador', 'Permite entrar a la vista desarrollador'), ('Vista_autor', 'Permite ingresar a la vista autor'), ('Vista_editor', 'Permite ingresar a la vista editor'), ('Vista_publicador', 'Permite ingresar a la vista publicador'), ('Vista_administrador', 'Permite ingresar a la vista administrador'), ('Editar usuarios', 'Permite editar la informacion de usuarios'), ('Ver usuarios', 'Permite ver la lista de usuarios'), ('Vista_tabla', 'Permite ver la tabla general'), ('Publicacion no moderada', 'Permite la publicacion en categorias no moderadas')]},
        ),
    ]