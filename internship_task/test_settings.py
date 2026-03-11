from .settings import *  # noqa

SECRET_KEY = "dummy-secret-for-tests"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Override database settings for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "inventory-sales-db",
        "USER": "postgres",
        "PASSWORD": "root",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# $ docker run -d \
#   --name inventory_sale_db \
#   -e POSTGRES_USER=postgres \
#   -e POSTGRES_PASSWORD=postgres \
#   -e POSTGRES_DB=inventory-sales-db \
#   -p 5432:5432 \
#   -v postgres_data:/var/lib/postgresql/data \
#   postgres:15-alpine
