# Generated by Django 4.2.4 on 2023-09-27 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contenido',
            name='razon_rechazo',
            field=models.TextField(blank=True, null=True),
        ),
    ]
