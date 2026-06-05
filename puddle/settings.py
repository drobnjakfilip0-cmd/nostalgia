from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Core ──────────────────────────────────────────────────────────────────────
SECRET_KEY    = os.environ['SECRET_KEY']
DEBUG         = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Auth ──────────────────────────────────────────────────────────────────────
LOGIN_URL             = 'core:login'
LOGIN_REDIRECT_URL    = 'core:index'
LOGOUT_REDIRECT_URL   = '/'
PASSWORD_RESET_TIMEOUT = 3600

# ── HTTPS / Cookie security ───────────────────────────────────────────────────
# In development (DEBUG=True) everything is OFF — plain HTTP works normally.
# In production (DEBUG=False) everything switches ON automatically.
if DEBUG:
    SECURE_SSL_REDIRECT            = False
    SESSION_COOKIE_SECURE          = False
    CSRF_COOKIE_SECURE             = False
    SECURE_HSTS_SECONDS            = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD            = False
else:
    SECURE_SSL_REDIRECT            = True
    SESSION_COOKIE_SECURE          = True
    CSRF_COOKIE_SECURE             = True
    SECURE_HSTS_SECONDS            = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD            = True

SECURE_CONTENT_TYPE_NOSNIFF    = True
X_FRAME_OPTIONS                = 'DENY'
SESSION_COOKIE_HTTPONLY        = True
CSRF_COOKIE_HTTPONLY           = True
SESSION_COOKIE_AGE             = 1209600  # 2 weeks

# ── Apps ──────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'axes',
    'core',
    'dashboard',
    'item',
    'conversation',
    'cloudinary',
    'cloudinary_storage',
]

# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

# ── Authentication backends ───────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ── django-axes ───────────────────────────────────────────────────────────────
AXES_FAILURE_LIMIT       = 5
AXES_COOLOFF_TIME        = 1
AXES_RESET_ON_SUCCESS    = True
AXES_USERNAME_FORM_FIELD = 'username'
AXES_LOCKOUT_CALLABLE    = 'core.views.locked_out'

# ── Rate limiting ─────────────────────────────────────────────────────────────
RATELIMIT_VIEW = 'core.views.ratelimited'

# ── URLs / Templates ──────────────────────────────────────────────────────────
ROOT_URLCONF = 'puddle.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'conversation.context_processors.inbox_badge',
            ],
        },
    },
]

WSGI_APPLICATION = 'puddle.wsgi.application'

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     'nostalgija',
        'USER':     'duborg_t',
        'PASSWORD': os.getenv('PASSWORD_DB'),
        'HOST':     'localhost',
        'PORT':     '5432',
        'CONN_MAX_AGE': 60,
    }
}

# ── Cache — Redis if available, else LocMemCache ──────────────────────────────
_REDIS_URL = os.environ.get('REDIS_URL', '')
if _REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': _REDIS_URL,
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
            'TIMEOUT': 300,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'TIMEOUT': 300,
        }
    }

# ── Password validators ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Storage ───────────────────────────────────────────────────────────────────
STORAGES = {
    'default': {
        'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUD_NAME'),
    'API_KEY':    os.getenv('API_KEY'),
    'API_SECRET': os.getenv('API_SECRET'),
}

# ── i18n ──────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ── Static & media ────────────────────────────────────────────────────────────
STATIC_URL  = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL   = 'media/'
MEDIA_ROOT  = BASE_DIR / 'media'

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@puddle.com')
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG
    else 'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST    = 'smtp.gmail.com'
EMAIL_PORT    = 587
EMAIL_USE_TLS = True
