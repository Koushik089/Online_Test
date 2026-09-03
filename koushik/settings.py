"""
Django settings for koushik project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-change-this-in-production'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'


# ============================================================
# ALLOWED HOSTS
# ============================================================

ALLOWED_HOSTS = [
    'onlinetest-omega.vercel.app',
    'localhost',
    '127.0.0.1',
]

# Allow all hosts during development
if DEBUG:
    ALLOWED_HOSTS = ['*']


# ============================================================
# CSRF
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    'https://onlinetest-omega.vercel.app',
]

if DEBUG:
    CSRF_TRUSTED_ORIGINS += [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'tokio',
    'voting',
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise for static files
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Student online/activity tracking
    'koushik.middleware.StudentActivityMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================================
# URL CONFIGURATION
# ============================================================

ROOT_URLCONF = 'koushik.urls'


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates',
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = 'koushik.wsgi.application'


# ============================================================
# DATABASE
#
# Production:
#     Supabase PostgreSQL
#
# Local:
#     MySQL if MYSQL_HOST exists
#
# Fallback:
#     SQLite
# ============================================================

if os.environ.get('POSTGRES_URL'):

    try:
        import dj_database_url

        DATABASES = {
            'default': dj_database_url.parse(
                os.environ.get('POSTGRES_URL'),
                conn_max_age=600,
                ssl_require=True,
            )
        }

    except ImportError:
        raise ImportError(
            'dj-database-url is required. '
            'Run: python -m pip install dj-database-url psycopg[binary]'
        )


elif os.environ.get('MYSQL_HOST'):

    try:
        import pymysql

        pymysql.install_as_MySQLdb()

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',

                'NAME': os.environ.get(
                    'MYSQL_NAME',
                    'exam_system_db'
                ),

                'USER': os.environ.get(
                    'MYSQL_USER',
                    'root'
                ),

                'PASSWORD': os.environ.get(
                    'MYSQL_PASSWORD',
                    ''
                ),

                'HOST': os.environ.get(
                    'MYSQL_HOST',
                    '127.0.0.1'
                ),

                'PORT': os.environ.get(
                    'MYSQL_PORT',
                    '3306'
                ),

                'OPTIONS': {
                    'init_command':
                        "SET sql_mode='STRICT_TRANS_TABLES'"
                },
            }
        }

    except ImportError:
        raise ImportError(
            'PyMySQL is required for MySQL database.'
        )


else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator',
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# WhiteNoise compressed static files
STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)


# ============================================================
# EMAIL CONFIGURATION
# ============================================================

EMAIL_BACKEND = (
    'django.core.mail.backends.smtp.EmailBackend'
)

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get(
    'EMAIL_HOST_USER',
    ''
)

EMAIL_HOST_PASSWORD = os.environ.get(
    'EMAIL_HOST_PASSWORD',
    ''
)

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ============================================================
# LOGIN
# ============================================================

LOGIN_URL = '/admin/login/'


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# PRODUCTION SECURITY
# ============================================================

if not DEBUG:

    SECURE_PROXY_SSL_HEADER = (
        'HTTP_X_FORWARDED_PROTO',
        'https'
    )

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_BROWSER_XSS_FILTER = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = 'DENY'