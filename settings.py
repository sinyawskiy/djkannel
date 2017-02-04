#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
# ! It is a good idea not to edit this and edit local_settings.py instead
# ! (copy local_settings.py.default to local_settings.py first)
# ! Especially if you want to update from version control system in future, because
# ! local_settings.py is not under version control

#DEBUG = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'mysql'        # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'smsmanager'       # Or path to database file if using sqlite3.
DATABASE_USER = 'satssmpp'               # Not used with sqlite3.
DATABASE_PASSWORD = '12345678'           # Not used with sqlite3.
DATABASE_HOST = ''               # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''               # Set to empty string for default. Not used with sqlite3.

DATABASES = {
 	'default': {
 	    'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smsmanager',
 	    'USER': 'satssmpp',
        'PASSWORD': '12345678',
        'HOST': '',
        'PORT': '',
 	}
}

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'media')
STATIC_URL = '/media/'

LOCALE_PATHS = (os.path.join(PROJECT_ROOT, 'locale'),)

AUTOCOMPLETE_ADMIN_MEDIA_PREFIX = '/media/admin/' # for widget autocomplete
AUTOCOMPLETE_MEDIA_PREFIX = '/media/autocomplete/'

# for model sms
SENDER = '79210000947'

SEND_EMAILS = False       # make it True and edit settings bellow if you want to receive emails
EMAIL_HOST = ''           # smtp.myhost.com
EMAIL_HOST_USER = ''      # user123
EMAIL_HOST_PASSWORD = ''  # qwerty
EMAIL_ADDRESS_FROM = ''   # noreply@myhost.com
if DEBUG:
    EMAIL_FAIL_SILENTLY = False
else:
    EMAIL_FAIL_SILENTLY = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ih^s_r3pgx!9-7aj%7^tqg#mj&zpdmchbbc=+*9=y#cm&v(ca)'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL= '/'

import sys, os
PROJECT_DIR = os.path.dirname(__file__)
sys.path.append(PROJECT_DIR)

TEMPLATE_DIRS = (
    PROJECT_DIR + '/templates/'
)

SITE_ID = 1
TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru-RU'
USE_I18N = True

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
#    'django.template.loaders.filesystem.load_template_source',
#    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'apps.todo.middleware.Custom403Middleware',
)
FILE_CHARSET = 'utf-8'

SESSION_SAVE_EVERY_REQUEST = False

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    
    # required by django-admin-tools, authority
    'django.core.context_processors.request',
    #'ort.annoying.context_processors.request_additions',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'urls'

KANNEL_DELIVER_PASSWORD = u'YM2H86DIB8'
KANNEL_DELIVER_USER = u'satssmsserver'

KANNEL_PASSWORD = u'Q8EM8Q1BJ5'
KANNEL_USER = u'satssmsgateway'
KANNEL_BEARERBOX_HOST = u'localhost'
KANNEL_SENDSMS_PORT =13013

INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',

    'pymorphy',
    
    'django.contrib.auth',
    #'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.admindocs',
    #'django.contrib.staticfiles',
    
    'autocomplete',
    #custom applications
    'recipients', #получатели, группы получателей
	'sms_storage', #хранилище смс, создание, редактирование
    'gateway'
)

#DATETIME_INPUT_FORMATS = '%d-%m-%y %H:%M:%S'
#DATETIME_FORMAT = 'd-m-y H:M:S'
# admin_tools
ADMIN_TOOLS_MEDIA_URL = '/media/'
ADMIN_TOOLS_INDEX_DASHBOARD ='dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD ='dashboard.CustomAppIndexDashboard'
ADMIN_TOOLS_MENU = 'menu.CustomMenu'
ADMIN_TOOLS_THEMING_CSS = 'admin_tools/css/theming.css'
#yandex maps
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = 'ortsmolny@yandex.ru'
EMAIL_HOST_PASSWORD = 'ftrnjhufpf2011'

PYMORPHY_DICTS = {
    'ru': {
        'dir': os.path.join(PROJECT_DIR, 'pymorphy_dicts', 'ru')
    },
    'en': {
        'dir': os.path.join(PROJECT_DIR, 'pymorphy_dicts', 'en')
    },
}

##################################################################################
# You can create local_settings.py to override the settings.
# It is recomended to put all your custom settings (database, path, etc.) there
# if you want to update from Subversion in future.
##################################################################################
try:
    from local_settings import *
except ImportError:
    pass

