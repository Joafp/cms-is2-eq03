# Generated by Django 4.2.4 on 2023-11-29 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('GestionCuentas', '0007_rol_borrado'),
        ('core', '0011_alter_contenido_autor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contenido',
            name='editor',
            field=models.ForeignKey(limit_choices_to={'roles__permisos__codename': 'Vista_editor'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contenidos_editor', to='GestionCuentas.usuariorol'),
        ),
        migrations.AlterField(
            model_name='contenido',
            name='publicador',
            field=models.ForeignKey(limit_choices_to={'roles__permisos__codename': 'Vista_publicador'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contenidos_publicador', to='GestionCuentas.usuariorol'),
        ),
    ]
