from myreadinglist.settings import *  # noqa F403

STATICFILES_STORAGE = ""
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
