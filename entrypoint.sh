#!/bin/sh

while ! nc -z db 5432; do
  echo "Waiting for database"
  sleep 2
done

echo "Confirming migration.."
flask db upgrade

echo "Starting server"
exec gunicorn -w 2 -k gevent --bind 0.0.0.0:80 "app:create_app()"

