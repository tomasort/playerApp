#!/bin/sh

celery -A playerApp.celery_app worker --loglevel INFO