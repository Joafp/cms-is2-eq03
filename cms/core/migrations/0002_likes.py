# Generated by Django 4.2.4 on 2023-10-29 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('GestionCuentas', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contenido', to='core.contenido')),
                ('user_dislikes', models.ManyToManyField(related_name='dislikes', to='GestionCuentas.usuariorol')),
                ('user_likes', models.ManyToManyField(related_name='likes', to='GestionCuentas.usuariorol')),
            ],
        ),
    ]
