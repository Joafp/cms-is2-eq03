# Generated by Django 4.2.4 on 2023-10-18 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermisosPer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': [('Boton desarrollador', 'Permite entrar a la vista desarrollador'), ('Vista_autor', 'Permite ingresar a la vista autor'), ('Vista_editor', 'Permite ingresar a la vista editor'), ('Vista_publicador', 'Permite ingresar a la vista publicador'), ('Vista_administrador', 'Permite ingresar a la vista administrador'), ('Editar usuarios', 'Permite editar la informacion de usuarios'), ('Ver usuarios', 'Permite ver la lista de usuarios'), ('Vista_tabla', 'Permite ver la tabla general')],
            },
        ),
        migrations.CreateModel(
            name='Rol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True)),
                ('permisos', models.ManyToManyField(default=None, to='auth.permission')),
            ],
        ),
        migrations.CreateModel(
            name='UsuarioRol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=100, unique=True, verbose_name='Nombre de usuario')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Correo electronico')),
                ('nombres', models.CharField(blank=True, max_length=200, null=True, verbose_name='Nombres')),
                ('apellidos', models.CharField(blank=True, max_length=200, null=True, verbose_name='Apellidos')),
                ('numero', models.IntegerField(blank=True, null=True, verbose_name='Numero')),
                ('usuario_activo', models.BooleanField(default=True)),
                ('usuario_administrador', models.BooleanField(default=False)),
                ('roles', models.ManyToManyField(to='GestionCuentas.rol')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
