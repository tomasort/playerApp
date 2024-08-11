#!/bin/sh

gunicorn -k gevent -w 1 -b 0.0.0.0:$FLASK_PORT playerApp:app