#!/bin/bash

# Exit immediately if any command returns a non-zero status
set -e

# Python-native check to wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL database container to boot..."
python3 -c "
import sys, socket, time
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect(('db', 5432))
        print('PostgreSQL is ready!')
        sys.exit(0)
    except socket.error:
        print('Postgres connection failed, retrying in 1s...')
        time.sleep(1)
"

# Run database schema migrations
echo "Running database migrations via Alembic..."
alembic upgrade head

# Start FastAPI server
echo "Starting Uvicorn API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
