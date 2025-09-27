#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create media directory for uploads
mkdir -p media
chmod 755 media

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser with new credentials
python create_superuser.py
