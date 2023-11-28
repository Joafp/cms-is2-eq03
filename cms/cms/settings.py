"""
Django settings for cms project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-pa9b5r^4-t15zljy=q8jjdv=zu*2p(ig^)bcf&b!(ba@$thc9f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    #App login
    'login.apps.LoginConfig',
    'GestionCuentas',
    'ckeditor',
    'django_seed',
]
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:81']
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cms.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'usuarios_cms',
        'USER': 'equipo3_admin',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}





# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Asuncion'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
import os
STATIC_URL = '/static/'
# STATIC_ROOT = '/home/joaquin/Escritorio/Proyectois2/cms-is2-eq03/cms/static'
STATIC_ROOT = '/home/mtx/proyectois2/cms-is2-eq03/cms/static'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL= 'MenuPrincipal'
from django.urls import reverse_lazy

LOGOUT_REDIRECT_URL=reverse_lazy('MenuPrincipal')
LOGIN_URL = reverse_lazy('login')
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
MEDIA_URL='/contenido_imagenes/'
# MEDIA_ROOT='/home/joaquin/Escritorio/Proyectois2/cms-is2-eq03/cms/media'
MEDIA_ROOT='/home/mtx/proyectois2/cms-is2-eq03/cms/media'

AWS_ACCESS_KEY_ID = 'AKIA2OAFYJVFS2RPPE45'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'backendcms'
AWS_S3_SIGNATURE_NAME = 's3v4',
AWS_S3_REGION_NAME = 'sa-east-1'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL =  None
AWS_S3_VERITY = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Para envio de emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Envia email a la consola
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
# EMAIL_PORT = 25 # Para envio por consola
EMAIL_PORT = 587
# EMAIL_HOST_USER = str(os.getenv('EMAIL_USER'))
# EMAIL_HOST_PASSWORD = str(os.getenv('EMAIL_PASSWORD'))
EMAIL_HOST_USER = 'is2cmseq03@gmail.com'
EMAIL_HOST_PASSWORD = 'zums pgkc etsa upgx'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Full',
    },
    'limite_caracteres': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Link', 'Unlink'],
        ],
        'maxLength': 200,  # Cambia 200 al número deseado de caracteres máximos
        'height': 100,
        'width': 600,
    },
}