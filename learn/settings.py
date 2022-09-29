import dj_database_url
import environ
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env(
    DEBUG=(bool, False)
)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# GENERAL
# ------------------------------------------------------------------------------

DEBUG = env.bool('DJANGO_DEBUG')
SECRET_KEY = env('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

# INTERNATIONALISATION
# ------------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# DATABASES
# ------------------------------------------------------------------------------

# For staging and prod, where Heroku PostgreSQL gives us a PostgreSQL URL in config vars
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(default=os.environ['DATABASE_URL'])
    }
# For local
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('POSTGRES_DB_NAME'),
            'ATOMIC_REQUESTS': True
        }
    }

# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# https://github.com/makinacorpus/django-safedelete
SAFE_DELETE_FIELD_NAME = 'deleted_at'

# URLS
# ------------------------------------------------------------------------------

# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'learn.urls'

# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'learn.wsgi.application'

# APPLICATIONS
# ------------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'polymorphic',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'compressor',
    'formtools',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'safedelete',
    'authentication',
    'staff',
    'student',
    'payment',
    'emails',
    'corsheaders',
]

# AUTHENTICATION
# ------------------------------------------------------------------------------

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = 'authentication.User'

# https://docs.djangoproject.com/en/4.0/ref/settings/#login-url
LOGIN_URL = '/staff/login/'

# PASSWORDS
# ------------------------------------------------------------------------------

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

# MIDDLEWARE
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
# ------------------------------------------------------------------------------

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3001",
]

CSRF_TRUSTED_ORIGINS = ['http://localhost:3001']

# STATIC
# https://docs.djangoproject.com/en/4.0/howto/static-files/
# https://docs.djangoproject.com/en/4.0/ref/settings/#settings-staticfiles
# ------------------------------------------------------------------------------

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# COMPRESS
# https://django-compressor.readthedocs.io/en/stable/quickstart.html
# ------------------------------------------------------------------------------
STATICFILES_FINDERS += ['compressor.finders.CompressorFinder']
COMPRESS_PRECOMPILERS = [('text/x-scss', 'django_libsass.SassCompiler')]
COMPRESS_CACHEABLE_PRECOMPILERS = (
    ("text/x-scss", "django_libsass.SassCompiler"))
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = env.bool('COMPRESS_OFFLINE')
COMPRESS_STORAGE = "compressor.storage.GzipCompressorFileStorage"
COMPRESS_URL = STATIC_URL

# SASS
# ------------------------------------------------------------------------------

SASS_PRECISION = 8

# TEMPLATES
# ------------------------------------------------------------------------------

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
                'django.template.context_processors.static'
            ],
        },
    },
]

# DJANGO REST FRAMEWORK
# https://www.django-rest-framework.org/
# ------------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

# DJANGO CRIPSY FORMS
# https://django-crispy-forms.readthedocs.io/en/latest/install.html
# ------------------------------------------------------------------------------

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# PAYMENT GATEWAYS
# ------------------------------------------------------------------------------

STRIPE = 'stripe'
STRIPE_ENDPOINT_SECRET = env('STRIPE_ENDPOINT_SECRET')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')

DOMAIN_URL = env('DOMAIN_URL')
SINGAPORE_DOLLAR_CURRENCY = 'sgd'

# SENDGRID
# ------------------------------------------------------------------------------

SENDGRID_API_KEY = env('SENDGRID_API_KEY')

# HUBSPOT
# ------------------------------------------------------------------------------

HUBSPOT_PRIVATE_APP_ACCESS_TOKEN = env('HUBSPOT_PRIVATE_APP_ACCESS_TOKEN')
BASICS_ENROLLED_FUNNEL_STATUS = 'basics_enrolled'

# SLACK
# ------------------------------------------------------------------------------

SLACK_USER_OAUTH_TOKEN = env('SLACK_USER_OAUTH_TOKEN')
SLACK_CODING_BASICS_WORKSPACE_INVITE_LINK = env('SLACK_CODING_BASICS_WORKSPACE_INVITE_LINK')

# SENTRY
# ------------------------------------------------------------------------------

# DSN tells SDK where to send events
SENTRY_DSN = env('SENTRY_DSN')

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[
        DjangoIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

# GLOBAL CONSTANTS
# ------------------------------------------------------------------------------

ROCKET_ACADEMY = 'Rocket Academy'
PROJECT_NAME = 'learn'
CODING_BASICS = 'CODING_BASICS'
CODING_BOOTCAMP = 'CODING_BOOTCAMP'
DAYS_BEFORE_BATCH_FOR_CREATING_SECTION_CHANNELS = 14
DAYS_BEFORE_BATCH_FOR_ADDING_STUDENTS_TO_SECTION_CHANNELS = 7
ISO_WEEK_DAYS = {
    'MON': '1',
    'TUE': '2',
    'WED': '3',
    'THU': '4',
    'FRI': '5',
    'SAT': '6',
    'SUN': '7'
}
PLACEHOLDER_PASSWORD = 'Placeholderpassw0rd!'

# FEES #
CODING_BASICS_REGISTRATION_FEE_SGD = 199

# DISCOUNTS #
CODING_BASICS_TIERED_DISCOUNT_PER_WEEK = 10
CODING_BASICS_TIERED_DISCOUNT_CAP = 40

# EMAILS #
ROCKET_CODING_BASICS_EMAIL = 'basics@rocketacademy.co'
ROCKET_COMMUNITY_EMAIL = 'community@rocketacademy.co'

# SENDGRID TEMPLATES #
CODING_BASICS_GRADUATION_NOTIFICATION_TEMPLATE_ID = env('CODING_BASICS_GRADUATION_NOTIFICATION_TEMPLATE_ID')
CODING_BASICS_REGISTRATION_CONFIRMATION_TEMPLATE_ID = env('CODING_BASICS_REGISTRATION_CONFIRMATION_TEMPLATE_ID')
COUPON_CODE_NOTIFICATION_TEMPLATE_ID = env('COUPON_CODE_NOTIFICATION_TEMPLATE_ID')
