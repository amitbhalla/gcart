# Setup Instructions

1. Make the folder -> `mkdir gcart`
2. Install Virual Envoirnment in the folder -> `python3 -m venv pyenv`
3. Activate the envoirnment -> `source pyenv/bin/activate`
4. Install the following packages
   - Install Black (For Pep8) `pip install black`
   - Install Flake8 (Linter) `pip install flake8`
   - Install Django (Main Framework) `pip install django`
   - Install Django Environ (for Django env variables) `pip install django-environ`
   - Install MySQLClient
     - Install the client `brew install mysql-client`
     - Push path to bash_profile `echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.bash_profile`
     - Echo the Path `export PATH="/usr/local/opt/mysql-client/bin:$PATH"`
     - Install the client `pip install mysqlclient`
   - Install Pillow (Needed for image mgmt) `pip install pillow`
5. Create gcartApp directory -> `mkdir gcartapp`
6. Push requirements to app directory -> `pip freeze > gcartapp/requirements.txt`

### Requirements.txt

```
amqp==5.0.6
asgiref==3.4.1
billiard==3.6.4.0
black==21.8b0
celery==5.1.2
certifi==2021.5.30
charset-normalizer==2.0.4
click==7.1.2
click-didyoumean==0.0.3
click-plugins==1.1.1
click-repl==0.2.0
Django==3.2.6
django-environ==0.4.5
flake8==3.9.2
idna==3.2
kombu==5.1.0
mccabe==0.6.1
mypy-extensions==0.4.3
mysqlclient==2.0.3
pathspec==0.9.0
Pillow==8.3.1
platformdirs==2.2.0
prompt-toolkit==3.0.20
pycodestyle==2.7.0
pyflakes==2.3.1
pytz==2021.1
razorpay==1.2.0
redis==3.5.3
regex==2021.8.28
requests==2.26.0
shortuuid==1.0.1
six==1.16.0
sqlparse==0.4.1
tomli==1.2.1
typing-extensions==3.10.0.1
urllib3==1.26.6
vine==5.0.0
wcwidth==0.2.5
```

7. Create docker-compose file in top directory

### local-docker.yml

```
version: "3.8"

services:
  gcartapp:
    build:
      context: .
      dockerfile: gcartapp/gcartapp.dockerfile
    volumes:
      - ./gcartapp:/gcartapp
      - ./gcartapp/container/media:/vol/web/media
      - ./gcartapp/container/static:/vol/web/static
    ports:
      - 8000:8000
    command: >
      sh -c "
      python manage.py wait_for_db &&
      python manage.py makemigrations &&
      python manage.py migrate &&
      python manage.py runserver 0.0.0.0:8000"
    depends_on:
      - db
      - redis
    links:
      - redis

  db:
    image: mysql:8.0
    volumes:
      - ./data:/var/lib/mysql
    env_file:
      - db/db.env

  phpmyadmin:
    image: phpmyadmin/phpmyadmin
    environment:
      - PMA_HOST=db
    depends_on:
      - db
    ports:
      - 8080:80

  redis:
    image: redis:6
    container_name: redis

  celery:
    build:
      context: .
      dockerfile: gcartapp/gcartapp.dockerfile
    volumes:
      - ./gcartapp:/gcartapp
    container_name: cl01
    command: celery -A core worker -l info
    links:
      - redis

networks:
  default:
    external:
      name: box-net

```

### production-docker.yml

```
version: "3"

services:
  gcartapp:
    build:
      context: .
      dockerfile: gcartapp/gcartapp.dockerfile
    volumes:
      - ./gcartapp:/gcartapp
      - ./gcartapp/container/media:/vol/web/media
      - ./gcartapp/container/static:/vol/web/static
    ports:
      - 8000:8000
    command: >
      sh -c "
      python manage.py wait_for_db &&
      python manage.py makemigrations &&
      python manage.py migrate &&
      python manage.py runserver 0.0.0.0:8000"
    depends_on:
      - redis
    links:
      - redis

  redis:
    image: redis:6
    container_name: redis

  celery:
    build:
      context: .
      dockerfile: gcartapp/gcartapp.dockerfile
    volumes:
      - ./gcartapp:/gcartapp
    container_name: cl01
    command: celery -A core worker -l info
    links:
      - redis

networks:
  default:
    external:
      name: box-net
```

8. Create db folder in main directory, so that gcartapp and db are in same folder.
9. Create db.env file and place it in the db folder. **Change the values below. Root password should not be same as user password.**

### db.env

```
MYSQL_DATABASE=gcartapp
MYSQL_USER=django
MYSQL_PASSWORD=!!CHANGE ME!!
MYSQL_ROOT_PASSWORD=!!CHANGE ME!!
```

10. Create gcartapp.dockerfile inside the app folder

### gcartapp.dockerfiles

```
FROM python:3.9.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /gcartapp
WORKDIR /gcartapp
COPY ./gcartapp/requirements.txt requirements.txt

RUN apk add --update --no-cache jpeg-dev mariadb-connector-c-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers musl-dev zlib zlib-dev

RUN pip install -r requirements.txt

RUN apk del .tmp-build-deps

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user
```

11. Run the build -> `docker-compose build --no-cache`
12. Create Django app -> `docker-compose run --rm gcartapp sh -c "django-admin startproject core ."`
13. Add pyproject.toml to root directory

### pyproject.toml

```
# Example configuration for Black.

# NOTE: you have to use single-quoted strings in TOML for regular expressions.
# It's the equivalent of r-strings in Python.  Multiline strings are treated as
# verbose regular expressions by Black.  Use [ ] to denote a significant space
# character.

[tool.black]
line-length = 79
target-version = ['py36', 'py37', 'py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # The following are specific to Black, you probably don't want those.
  | blib2to3
  | tests/data
  | profiling
)/
'''


# Build system information below.
# NOTE: You don't need this in your own Black configuration.

[build-system]
requires = ["setuptools>=41.0", "setuptools-scm", "wheel"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
# Option below requires `tests/optional.py`
optional-tests = [
  "no_python2: run when `python2` extra NOT installed",
  "no_blackd: run when `d` extra NOT installed",
  "no_jupyter: run when `jupyter` extra NOT installed",
]
```

14. Add flake8 config file to gcartapp directory

### .flake8

```
[flake8]
exclude =
    migrations,
    __pycache__,
    manage.py,
    settings.py
```

15. Create a new .env file inside gcartapp/core folder

### gcartapp/core/.env

```
SECRET_KEY=KET
DB_HOST=db
DB_NAME=gcartapp
DB_USER=root
DB_PASSWORD=!!CHANGE ME!!
PORT=3306
EMAIL_HOST=!!CHANGE ME!!
EMAIL_USE_TLS=True
EMAIL_PORT=25
RAZORPAY_ID=!!CHANGE ME!!
RAZORPAY_SECRET=!!CHANGE ME!!
SENDER_EMAIL=!!CHANGE ME!!
```

Note: Shifted to root user since test needs access to create database

16. Edit the settings.py inside core folder to use env variables

### settings.py

```
import environ

env = environ.Env()
environ.Env.read_env()

...

SECRET_KEY = env("SECRET_KEY")

...

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": env("DB_HOST"),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "PORT": env("PORT"),
    }
}

...

STATIC_URL = "/static/"
STATIC_ROOT = "/vol/web/static"
MEDIA_URL = "/media/"
MEDIA_ROOT = "/vol/web/media"
```

17. Edit the urls.py in core folder

### urls.py

```
from django.conf.urls.static import static
from django.conf import settings

...

urlpatterns = [

  ...

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

```

18. In Models when refering to file locations use this code

```
import os
import uuid

...

""" Custom Function to be duplicated for each file field in a model"""
def thumbnail_file_location(instance, filename):
    """Generate file path for a resource"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("upload/images/", filename)

...

thumbnail = models.ImageField(upload_to=thumbnail_file_location)
```

19. Import .gitignore
20. Setup git and initial commit.
21. Start the application `docker-compose up -d`

---

# Misc Commands
