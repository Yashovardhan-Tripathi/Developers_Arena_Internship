from .settings import *  # noqa: F403

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
CHANNEL_LAYERS = {'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}
REST_FRAMEWORK = {**REST_FRAMEWORK, 'DEFAULT_THROTTLE_CLASSES': [], 'DEFAULT_THROTTLE_RATES': {'anon': '10000/hour', 'user': '10000/hour', 'login': '10000/minute'}}

CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
