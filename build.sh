#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install the tools using the explicit python module
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 2. Prepare the database and static files
python manage.py collectstatic --no-input
python manage.py migrate