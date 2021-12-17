#! /usr/bin/env bash
set -e


# Let the DB start
python backend_pre_start.py

# Run migrations
alembic upgrade head

gunicorn --reload -c gunicorn_conf.py


# Create initial data in DB
#python /app/app/initial_data.py
