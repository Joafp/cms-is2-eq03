# Generated by Django 4.2.4 on 2023-10-06 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('GestionCuentas', '0001_initial'),
        ('core', '0007_contenido_ultimo_publicador'),
    ]

    operations = [
        migrations.AddField(
            model_name='contenido',
            name='editor',
            field=models.ForeignKey(default=1, limit_choices_to={'roles__nombre': 'Editor'}, on_delete=django.db.models.deletion.CASCADE, related_name='contenidos_editor', to='GestionCuentas.usuariorol'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contenido',
            name='publicador',
            field=models.ForeignKey(default=1, limit_choices_to={'roles__nombre': 'Publicador'}, on_delete=django.db.models.deletion.CASCADE, related_name='contenidos_publicador', to='GestionCuentas.usuariorol'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contenido',
            name='autor',
            field=models.ForeignKey(limit_choices_to={'roles__nombre': 'Autor'}, on_delete=django.db.models.deletion.CASCADE, related_name='contenidos_autor', to='GestionCuentas.usuariorol'),
        ),
    ]
