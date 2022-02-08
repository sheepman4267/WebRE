"""
Django settings for WebRE project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path
import os

def strToBool(string):
    d = {'True': True, 'False': False}
    return d.get(string, string)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

try:
    PRODUCTION = strToBool(os.environ['WEBRE_IN_PRODUCTION'])
except:
    PRODUCTION = False
DEBUG = not PRODUCTION

try:
    SECRET_KEY = os.environ['WEBRE_SECRET_KEY']
except KeyError: #If we're running in production, fail with no secret key. Otherwise, do what you like.
    if PRODUCTION:
        raise ImproperlyConfigured('No Secret Key found! Specify one with the environmental variable "WEBRE_SECRET_KEY".')
    else:
        SECRET_KEY = 'django-insecure-53!-(dsf5a!w_a@^&#r7f*7yo4fol^w#nj_a)1%db6c&2p+5-2'

if PRODUCTION:
    try:
        ALLOWED_HOSTS = os.environ['WEBRE_ALLOWED_HOSTS'].split(',')
    except KeyError:
        if PRODUCTION:
            raise ImproperlyConfigured('No Allowed Hosts specified. Specify them, comma-separated, in the environmental variable "WEBRE_ALLOWED_HOSTS".')
        else:
            ALLOWED_HOSTS = []

    try:
        CSRF_TRUSTED_ORIGINS = os.environ['WEBRE_CSRF_TRUSTED_ORIGINS'].split(',')
    except KeyError:
        if PRODUCTION:
            raise ImproperlyConfigured('No CSRF Trusted Origins Configured. Specofy them, comma-separated, in the environmental variable "WEBRE_CSRF_TRUSTED_ORIGINS".')
        else:
            CSRF_TRUSTED_ORIGINS = []

if PRODUCTION: #Change this later to allow for other DB backends, probably
    ALLOWED_HOSTS = ["webre.uubloomington.org"]
    try:
        db_password = os.environ['WEBRE_POSTGRES_PASSWORD']
    except KeyError:
        raise ImproperlyConfigured('No PostgrSQL Password specified! Specify one with the environment variable "WEBRE_POSTGRES_PASSWORD".')
    try:
        db_service = os.environ['WEBRE_POSTGRES_SERVICE']
    except KeyError:
        raise ImproperlyConfigured('No PostgreSQL Service specified! Specify one with the environment variable "WEBRE_POSTGRES_SERVICE".')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'OPTIONS': {
                'service': db_service,
                'password': db_password,
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


try:
    STATIC_ROOT = os.environ['WEBRE_STATIC_ROOT']#"/var/www/webre.uubloomington.org"
except KeyError:
    if PRODUCTION:
        raise ImproperlyConfigured('No Static Root configured! Use the environmental variable "WEBRE_STATIC_ROOT".')
    else:
        STATIC_ROOT = './staticfiles'

# Quick-start development settings - unsuitable for production
# See

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!

# Application definition

INSTALLED_APPS = [
    'classroom.apps.ClassroomConfig',
    'markdownx',
    'colorfield',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'WebRE.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'WebRE.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Indiana/Indianapolis'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'

