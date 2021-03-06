"""
Django settings for labonclick project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR.joinpath('templates')
MEDIA_ROOT = BASE_DIR.joinpath('media')


#Comment for docker deployment
#STATIC_DIR = BASE_DIR.joinpath('static')

# Uncomment for docker deployment
STATIC_ROOT = BASE_DIR.joinpath('static')


DEFAULT_AUTO_FIELD='django.db.models.AutoField'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Uncomment for docker dep
SECRET_KEY =  os.environ.get("SECRET_KEY")

# Commment for docker dep
#SECRET_KEY = 'K5Hza3YBp6WjPcy7'

# SECURITY WARNING: don't run with debug turned on in production!

# Uncomment for docker dep
DEBUG = os.environ.get("DEBUG", default=1)

# Comment for docker deployment
#DEBUG = 1
ALLOWED_HOSTS = ['*']

#ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.user_sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'resource_manager',
    'django_filters',
    'bootstrap5',
    'django_celery_results',
    'ckeditor',
    'rest_framework',
    'celery_progress',
    'simple_history',
]


# CELERY STUFF
BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Istanbul'
#CELERY_RESULT_BACKEND = 'django-db'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'labonclick.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'labonclick.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

#DATABASES = {
#    'default': {
#        "ENGINE": 'django.db.backends.postgresql_psycopg2',
#        "NAME": 'labmanager',
#        "USER": 'dbuser',
#        "PASSWORD": '$SatCom$',
#        "HOST": 'localhost',
#        "PORT": '5432',
#    }
#}

# for docker deployment
DATABASES = {
     'default': {
         "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
         "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
         "USER": os.environ.get("SQL_USER", "user"),
         "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
         "HOST": os.environ.get("SQL_HOST", "localhost"),
         "PORT": os.environ.get("SQL_PORT", "5432"),
     }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]


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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
#STATIC_ROOT = STATIC_DIR
STATIC_URL = '/static/'

# Comment for docker dep
#STATICFILES_DIRS = [
#   STATIC_DIR,
#]

# MEDIA_DIR
MEDIA_URL = '/media/'
#MEDIA_ROOT = MEDIA_DIR

LOGIN_URL = 'resource_manager/user_login'