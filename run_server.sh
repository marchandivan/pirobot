#!/bin/bash

NAME="picaterpillar"                              #Name of the application (*)
BASEDIR=$(dirname "$0")
BASEDIR=$(cd $BASEDIR; pwd)

DJANGODIR=$BASEDIR/webserver/picaterpillar        # Django project directory (*)
USER=www-data                                     # the user to run as (*)
GROUP=webdata                                     # the group to run as (*)
NUM_WORKERS=2                                     # how many worker processes should Gunicorn spawn (*)
DJANGO_SETTINGS_MODULE=$NAME.settings             # which settings file should Django use (*)
DJANGO_WSGI_MODULE=$NAME.wsgi                     # WSGI module name (*)

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR

# Set Volume to 100%
amixer -c 0 set Headphone 100%

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /usr/local/bin/pipenv run python manage.py runserver 0.0.0.0:8000
