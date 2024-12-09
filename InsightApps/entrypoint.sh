#!/bin/sh

# Check and apply migrations for each app
python manage.py makemigrations dashboard || exit 1
python manage.py migrate dashboard || exit 1

python manage.py makemigrations quickbooks || exit 1
python manage.py migrate quickbooks || exit 1

python manage.py makemigrations copilot || exit 1
python manage.py migrate copilot || exit 1

python manage.py makemigrations sample || exit 1
python manage.py migrate sample --database=example || exit 1

# Apply any remaining migrations
python manage.py migrate || exit 1

# Import data if migrations were successful
if [ $? -eq 0 ]; then
    python manage.py import_employees paths/employees.json || exit 1
    python manage.py import_data || exit 1
fi

exec "$@"
