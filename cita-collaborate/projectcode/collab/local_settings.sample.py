DEBUG = False
TEMPLATE_DEBUG = DEBUG



ADMINS = (
     ('Administrator', 'admin@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
#DATABASE_OPTIONS = {"init_command": "SET storage_engine=INNODB"}
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
ADMIN_MEDIA_PREFIX = ''

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "",
)

# Specifies the number of days to wait for the user to verify account creation!
ACCOUNT_ACTIVATION_DAYS = 30
REGISTRATION_FROM_EMAIL = 'register@example.com'
CONTACT_FROM_EMAIL = 'do_not_reply@example.com'
DEFAULT_FROM_EMAIL = 'admin@example.com'

# For Django Logging
if DEBUG:
    INTERNAL_IPS = ('127.0.0.1',)
