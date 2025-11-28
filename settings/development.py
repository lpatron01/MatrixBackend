from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

