# Generated by Django 4.2.4 on 2023-11-28 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_reporte_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contenido',
            name='fecha_publicacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]