#!/bin/bash
set -e

cd "$(dirname "$0")"

# Remove DB and all migration versions
rm -f test.db
rm -f alembic/versions/*.py

# Generate new initial migration
alembic revision --autogenerate -m "initial"

# Apply migrations
alembic upgrade head

# Seed admin, widgets, menu, schedules
python app/create_admin_user.py

echo "Database reset, migrated, and seeded."
