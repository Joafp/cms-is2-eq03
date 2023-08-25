# Generated by Django 3.2.12 on 2023-08-23 16:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('GestionCuentas', '0005_alter_permisosper_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuariorol',
            name='user_inicio',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
    ]