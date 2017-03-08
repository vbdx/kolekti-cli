"""
Django settings for kolekti_server project.

Generated by 'django-admin startproject' using Django 1.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9ewjmy&i^@0kgd6(bapt%@azcl2wka6ml^tcs9v*9@-2%705#y'

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = (os.getenv('KOLEKTI_DEBUG',"") == "True")
if DEBUG:
    HOSTNAME='0.0.0.0'
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
else:
    HOSTNAME=os.getenv('VIRTUAL_HOST','localhost.localdomain')
    ALLOWED_HOSTS='*'

SITE_ID = 1 

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
    )

ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED=True
ACCOUNT_EMAIL_VERIFICATION="mandatory"
ACCOUNT_ADAPTER = 'invitations.models.InvitationsAdapter'
INVITATIONS_ALLOW_JSON_INVITES = True
INVITATIONS_ACCEPT_INVITE_AFTER_SIGNUP = True

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'bootstrapform',
#    'registration',
    'kserver',
    'kserver_saas',
    'translators',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'invitations',
    'django.contrib.admin',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'kserver_saas.views.KolektiSaasMiddleware',
    )

ROOT_URLCONF = 'kolekti_server.urls'

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

WSGI_APPLICATION = 'kolekti_server.wsgi.application'



# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'fr-FR'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

if os.sys.platform[:3] == "win":
    STATIC_PATH="kserver/static/"
else:
    STATIC_PATH="kolekti_server/kserver/static/"
    
from kolekti.settings import settings as kolekti_settings
KOLEKTI_CONFIG = kolekti_settings()

def __get_config(env, section, item): 
    try:
        VALUE = os.environ[env]
    except:
        try:
            VALUE = KOLEKTI_CONFIG.get(section).get(item,'')
        except:
            VALUE = ''
    return VALUE


if os.sys.platform[:3] == "win":
    appdatadir = os.path.join(os.getenv("APPDATA"),'kolekti')
    DB_NAME = appdatadir + '\\db.sqlite3'
    DB_NAME = DB_NAME.replace('\\','/')
else:
    DB_NAME = __get_config('KOLEKTI_DBFILE','InstallSettings','database_dir')
    #DB_NAME = os.path.join(DB_DIR, 'db.sqlite3')


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_NAME,
    }
}

ACCOUNT_ACTIVATION_DAYS = 7;
    
KOLEKTI_BASE = __get_config('KOLEKTI_BASE','InstallSettings','projectspath')
KOLEKTI_SVN_ROOT = __get_config('KOLEKTI_SVN_ROOT','InstallSettings','svnroot')
KOLEKTI_SVN_PASSFILE = __get_config('KOLEKTI_SVN_PASSFILE','InstallSettings','svnpassfile')
KOLEKTI_SVN_GROUPFILE = __get_config('KOLEKTI_SVN_GROUPFILE','InstallSettings','svngroupfile')
KOLEKTI_LANGS = ['fr','en','us','de','it']
KOLEKTI_SVNTPL_USER = __get_config('KOLEKTI_SVNTPL_USER','SvnRemotes','svnuser')
KOLEKTI_SVNTPL_PASS = __get_config('KOLEKTI_SVNTPL_PASS','SvnRemotes','svnpass')

if os.sys.platform[:3] == "win":
    KOLEKTI_MULTIUSER = False
else:
    KOLEKTI_MULTIUSER = True
    
KOLEKTI_AUTOSYNC = False
RE_BROWSER_IGNORE=["~$","^\.svn$", "^#.*#$"]

email_config = KOLEKTI_CONFIG.get('smtp_ssl')
if email_config is None:
    email_config = {}

EMAIL_HOST = os.getenv('KOLEKTI_EMAIL_HOST',email_config.get('host',''))
EMAIL_PORT = os.getenv('KOLEKTI_EMAIL_PORT',email_config.get('port',''))
EMAIL_HOST_USER = os.getenv('KOLEKTI_EMAIL_USER',email_config.get('user',''))
EMAIL_HOST_PASSWORD = os.getenv('KOLEKTI_EMAIL_PASSWORD',email_config.get('pass',''))
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
DEFAULT_FROM_EMAIL = os.getenv('KOLEKTI_EMAIL_FROM',email_config.get('from',''))

LOG_PATH = os.path.join(KOLEKTI_BASE,'.logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'console': {
            'format': '[%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_PATH, 'debug.log'),
            'formatter':'verbose',
        },
        'file_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_PATH, 'info.log'),
            'formatter':'simple',
        },
        'file_kolekti': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_PATH, 'kolekti.log'),
            'formatter':'verbose',
        },
        'console_kolekti': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter':'console',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.info': {
            'handlers': ['file_info'],
            'level': 'INFO',
            'propagate': True,
        },
        'kolekti': {
            'handlers': ['file_kolekti'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
