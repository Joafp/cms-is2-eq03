# Generated by Django 3.2.12 on 2023-08-23 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GestionCuentas', '0006_usuariorol_user_inicio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuariorol',
            name='user_inicio',
        ),
    ]