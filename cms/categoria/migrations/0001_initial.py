# Generated by Django 4.2.4 on 2023-09-03 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('moderada', models.BooleanField(default=False)),
                ('activo', models.BooleanField(default=True)),
            ],
        ),
    ]
