#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- 🏛️ STARTING NATIONAL HUB BUILD ---"

# 1. Force installation into the global environment
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "--- 📊 RUNNING REGISTRY MIGRATIONS ---"
python manage.py collectstatic --no-input
python manage.py migrate

echo "--- ✅ BUILD COMPLETE ---"