# Generated by Django 4.2.4 on 2023-10-07 20:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GestionCuentas', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='permisosper',
            options={'permissions': [('Boton desarrollador', 'Permite entrar a la vista desarrollador'), ('Vista autor', 'Permite ingresar a la vista autor'), ('Vista editor', 'Permite ingresar a la vista editor'), ('Vista publicador', 'Permite ingresar a la vista publicador'), ('Vista administrador', 'Permite ingresar a la vista administrador'), ('Editar usuarios', 'Permite editar la informacion de usuarios'), ('Ver usuarios', 'Permite ver la lista de usuarios'), ("Vista tabla'", 'Permite ver la tabla general')]},
        ),
    ]
