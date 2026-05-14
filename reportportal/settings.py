from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = '0tn1!1!w$q29%)gu%w^^q3ajp^4)(=_=x=u*1u0#u++1tz4f-t'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'reports',
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

ROOT_URLCONF = 'reportportal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'reportportal.wsgi.application'

# ─── DATABASE ─────────────────────────────────────────────────────────────────
# MySQL configuration.
# Set via environment variables (recommended) or edit directly for dev.
#
#   DB_NAME      → MySQL database name  (default: reportportal_db)
#   DB_USER      → MySQL username       (default: root)
#   DB_PASSWORD  → MySQL password       (default: '')
#   DB_HOST      → MySQL host           (default: localhost)
#   DB_PORT      → MySQL port           (default: 3306)
#
# Install: pip install mysqlclient
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'reportportal'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'Navya@2005'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

# Email settings
USE_EMAIL_API = True

EMAIL_API_URL = 'https://support.ncmrwf.gov.in/mail/api_send_email_reports'
# EMAIL_API_KEY = 'your-api-key-here'   # only if the API requires a key

# Django SMTP fallback (used when the NCMRWF API is unreachable, e.g. local dev)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ramyanavya02@gmail.com'
EMAIL_HOST_PASSWORD = 'qcwd eyqm qqcc vuqw'
DEFAULT_FROM_EMAIL = 'ReportPortal <ramyanavya02@gmail.com>'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Secret used by the frontend AES encryption for PDF display names.
PDF_FILENAME_SECRET = os.environ.get('PDF_FILENAME_SECRET', 'reportportal-pdf-secret-key-2024')

# Session / CSRF cookie settings — fixes CSRF token mismatch on OTP page
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = True
