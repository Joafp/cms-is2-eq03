# Generated by Django 4.2.4 on 2023-09-28 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_contenido_razon_rechazo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contenido',
            name='razon_rechazo',
        ),
    ]
