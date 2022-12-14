# Dockerise a Django project - Part 3

Welcome to Part 3 of the series on how we set up and dockerise every new Django project at Webinative.

In part 1, we created a new Django project with a core app and custom User model.

In part 2, we added some useful third-party Django apps and python packages to our project.

This article will focus on abstracting some key configurations into environment variables.

## Why use environment variables

In a typical organisation, we run a Django project in one or more of the following environments,

- Alpha   (Development)
- Beta    (Quality assurance)
- Staging (Pre-Production)
- Live    (Production)

Some of the project's configurations/settings change depending on the runtime environment. For example, consider the `ALLOWED_HOSTS` and `DEBUG` values.

| Setting | Alpha | Beta | Staging | Live |
| --- | --- | --- | --- | --- |
| `ALLOWED_HOSTS` | `localhost` | `beta.myproject.com` | `staging.myproject.com` | `myproject.com` |
| `DEBUG` | `True` | `True` | `False` | `False` |

Moreover, it is good practice to have a unique `SECRET_KEY` for every environment.

The old-school approach is to have multiple `settings.py` files &mdash; one for each environment like `settings_alpha.py`, `settings_beta.py`, etc. But saving your secrets in Git or any VCS is not recommended (see [12-factor principles](https://12factor.net/)). A better approach is to use environment variables.

## Abstract ENV variables

Create a `.env` file within your project root (same level as `manage.py`).

> **Note**: Files and folders starting with a dot in their name remain hidden in Linux and Mac.

We'll identify the config that could change with environments and move them into this file.

```ini
# contents of .env

DJANGO_ALLOWED_CIDR_NETS=192.168.0.0/24
DJANGO_ALLOWED_HOSTS=localhost
DJANGO_DEBUG=True
DJANGO_INTERNAL_IPS=127.0.0.1
DJANGO_TIME_ZONE=UTC
DJANGO_SECRET_KEY="django-insecure-q-*lrcfa-ll41wh@9=l+f=96%!9%vpm8h)jdw)gpw7)i41c94k"
```

> **Note**: The prefix `DJANGO_` acts as a namespace for these ENV vars.

Next, we'll update `settings.py` to read these values from the environment.

```python
import os

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

DEBUG = os.getenv('DJANGO_DEBUG')

ALLOWED_HOSTS = []
ALLOWED_HOSTS_ENV = os.getenv('DJANGO_ALLOWED_HOSTS')
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = ALLOWED_HOSTS_ENV.split(',')

if DEBUG:
    ALLOWED_CIDR_NETS_ENV = os.getenv('DJANGO_ALLOWED_CIDR_NETS')
    if ALLOWED_CIDR_NETS_ENV:
        ALLOWED_CIDR_NETS = ALLOWED_CIDR_NETS_ENV.split(',')

    INTERNAL_IPS_ENV = os.getenv('DJANGO_INTERNAL_IPS')
    if INTERNAL_IPS_ENV:
        INTERNAL_IPS = INTERNAL_IPS_ENV.split(',')

# ...

TIME_ZONE = os.getenv('DJANGO_TIME_ZONE', 'UTC')
```

**Tip:** Adding the `.env` file to our project's `.gitignore` ensures Git doesn't track this file.

Now, try running the development server.

```sh
# within your project folder

workon dockerise_django

./manage.py runserver 0:8000
```

You should see an error as shown below,

![runserver without env vars](images/part_3/01-runserver_without_env.png)

Why? We have abstracted some settings into a `.env` file but not loaded them into our virtual environment.

### Load ENV variables

Let us load the contents of the `.env` file into our virtual environment and then run the development server.

```sh
# load contents of .env file
set -o allexport; source .env; set +o allexport

# runserver
./manage.py runserver 0:8000
```

![runserver with env vars](images/part_3/02-runserver_with_env.png)

The development server now runs without errors.

**Tip:** You can use the `postactivate` hook to load the `.env` file every time the virtual environment is activated.

Add the following lines to the `$WORKON_HOME/dockerise_django/bin/postactivate` file.

```sh
set -o allexport; source $HOME/Dev/dockerise-django/.env; set +o allexport
```

You can test the `postactivate` hook using the following commands,

```sh
deactivate

workon dockerise_django

echo $DJANGO_ALLOWED_HOSTS
# should print localhost

./manage.py runserver 0:8000
# should run the dev server without any errors
```

As you move forward and add more apps to your project, remember to identify and abstract environment-specific configuration into the `.env` file.

In the next part, we will start containerising the application.
