#!/bin/bash

# Ожидание готовности базы данных
until pg_isready -h db -p 1221 -U username; do
  echo "Ожидание готовности базы данных..."
  sleep 2
done

# Применение миграций Alembic
alembic upgrade head

# Запуск приложения
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000  --log-level debug
