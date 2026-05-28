#!/bin/sh

nginx -g "pid $(pwd)/nginx.pid;"
gunicorn -c gunicorn_conf.py app:app
