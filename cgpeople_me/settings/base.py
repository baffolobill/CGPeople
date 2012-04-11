from unipath import FSPath as Path

PROJECT_ROOT = Path(__file__).absolute().ancestor(2)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ("Lex", "baffolobill@yandex.ru"),
)
DEFAULT_FROM_EMAIL = 'no-reply@cgpeople.me'

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": 'cgpeople_me',
        "USER": 'postgres',
        "PASSWORD": 'postgres',
        "HOST": 'localhost',
        "PORT": '5432',
    }
}

TIME_ZONE = "America/Los_Angeles"
LANGUAGE_CODE = "en-us"
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = Path(PROJECT_ROOT.ancestor(1), "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = Path(PROJECT_ROOT.ancestor(1), "static0")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = u"%s%s" % (STATIC_URL, "admin/")

# Additional locations of static files
STATICFILES_DIRS = (
    Path(PROJECT_ROOT, "static"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = "005r#q$9jn$n$8gv&nz@&07318v(mao(1w9*6===yo6bcfnaq6"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

ROOT_URLCONF = "urls"

TEMPLATE_DIRS = (
    Path(PROJECT_ROOT, "templates"),
)

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/p/%s/" % o.username,
}

DJANGO_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    'django.contrib.gis',
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
)

THIRD_PARTY_APPS = (
    "south",
    #"floppyforms",
    #"crispy_forms",
    "twitter_users",
    "generic",
    "machinetags",
    "cities",
    "taggit",
    #"django_messages",
    "threaded_messages",
    "markdown_deux",
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler"
        }
    },
    "loggers": {
        #'cities': {
        #    'handlers': ['console'],
        #    'level': 'INFO',
        #},
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },

    }
}

CLOUDMADE_API_KEY = '7480e4f340004f308c3dbe4db0806773'

AUTHENTICATION_BACKENDS = (
    'twitter_users.backends.TwitterBackend',
    # Uncomment the next line if you want to also allow password auth
    'django.contrib.auth.backends.ModelBackend',
)

TWITTER_KEY = 'bjmpox9oC3nuekRccqsnw'
TWITTER_SECRET = 'Pydbz9hXTQLL7G2bdzXfhzUdr5ZS9D13lKjER0krRAg'
#LOGIN_REDIRECT_VIEW = 'profile-edit'
LOGIN_REDIRECT_URL = '/profile/'

CITIES_LOCALES = ['en', 'und']
CITIES_POSTAL_CODES = ['US','CA']
CITIES_FILES = {
    # Uncomment below to import all cities with population > 1000 (default is > 5000)
    'city': {
       'filename': 'cities1000.zip',
       'urls':     ['http://download.geonames.org/export/dump/'+'{filename}']
    },
}
CITIES_PLUGINS = [
    'cities.plugin.postal_code_ca.Plugin',  # Canada postal codes need region codes remapped to match geonames
]
