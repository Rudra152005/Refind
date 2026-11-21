#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Collect static files into staticfiles/
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Seed default admin, student accounts, and demo campus listings
python manage.py seed_data
