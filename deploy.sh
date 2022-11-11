#!bin/bash

cd /home/ubuntu/thatcomputerscientist
pwd
git pull
python3 manage.py migrate
python3 manage.py makemigrations
cp ../.env .
pkill gunicorn
gunicorn --bind :8000 --workers 2 thatcomputerscientist.wsgi --daemon
