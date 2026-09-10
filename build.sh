#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Compile static assets
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Load initial categories, products, and admin user
if [ -f initial_data.json ]; then
    python manage.py loaddata initial_data.json
fi

# Ensure default admin superuser exists
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

