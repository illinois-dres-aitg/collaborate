# Django settings for collab project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Administrator', 'mueen@nawaz.org'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_OPTIONS = {}
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'j&zb3b8j@z-b1zmcwclj-$#n$xdc*bzp%uf$_-)#a)_havz-m9'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'collab.collab_middleware.CheckProfileExistence', 
    'collab.collab_middleware.RemoveAnonymousMessage', 
    'djangologging.middleware.LoggingMiddleware', 
)

ROOT_URLCONF = 'collab.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "",
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.markup', 
    'collab.registration', 
    'django.contrib.admin', 
    'collab.profiles', 
    'collab.project', 
    'collab.teleconference', 
    'collab.action',
    'collab.issues',
    'collab.templatetags', 
    'collab.siteinfo', 
    'django.contrib.comments', 
    'django_evolution',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "collab.context_processors.root_url",
    "django.core.context_processors.auth",
    "collab.context_processors.message_to_anonymous", 
    "collab.context_processors.add_subscribe_menu", 
    "collab.context_processors.breadcrumbs", 
    "collab.context_processors.announce_privilege", 
    "collab.context_processors.menu_privileges", 
    "collab.context_processors.announce_expired",
    "collab.context_processors.time_zone",
    "collab.context_processors.login_url_with_redirect",
    "collab.context_processors.site_announcements",
    "collab.context_processors.add_year",
    #"collab.contact_form",
)


AUTH_PROFILE_MODULE = "profiles.UserProfile"
LOGIN_REDIRECT_URL = "/projects/"
LOGIN_URL = "/accounts/login/"
LOGOUT_URL = "/accounts/logout/"


# For Django-logging.
#LOGGING_OUTPUT_ENABLED = DEBUG
#LOGGING_LOG_SQL = True
#LOGGING_INTERCEPT_REDIRECTS = DEBUG



# Specifies the number of days to wait for the user to verify account creation!
ACCOUNT_ACTIVATION_DAYS = 30
REGISTRATION_FROM_EMAIL = 'register@example.com'
CONTACT_FROM_EMAIL = 'do_not_reply@example.com'
DEFAULT_FROM_EMAIL = ''

# For Django Logging
if DEBUG:
    INTERNAL_IPS = ('127.0.0.1',)


MAX_IMAGE_SIZE = 2*1024*1024

try:
    from local_settings import *
except ImportError:
    pass

