import environ
import os

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
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

# HUBSPOT
# ------------------------------------------------------------------------------

HUBSPOT_PRIVATE_APP_ACCESS_TOKEN = env('HUBSPOT_PRIVATE_APP_ACCESS_TOKEN')

# PAYMENT GATEWAYS
# ------------------------------------------------------------------------------

STRIPE = 'stripe'
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_ENDPOINT_SECRET = env('STRIPE_ENDPOINT_SECRET')

DOMAIN_URL = env('DOMAIN_URL')
SINGAPORE_DOLLAR_CURRENCY = 'sgd'

# SENDGRID
# ------------------------------------------------------------------------------

SENDGRID_API_KEY = env('SENDGRID_API_KEY')

# GLOBAL CONSTANTS
# ------------------------------------------------------------------------------

CODING_BASICS = 'CODING_BASICS'
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

# EMAILS #
ROCKET_EMAIL = 'engineering@rocketacademy.co'
CODING_BASICS_REGISTRATION_CONFIRMATION_TEMPLATE_ID = 'd-0fc0a2398ba044a0b5015a528460bd3d'
