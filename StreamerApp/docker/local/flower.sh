#!/bin/sh

celery -A playerApp.celery_app flower --port=$FLOWER_PORT