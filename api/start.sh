#!/bin/sh

nginx
gunicorn -c gunicorn_conf.py app:app
