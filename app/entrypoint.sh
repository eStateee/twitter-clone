#!/bin/sh

mkdir -p ./alembic/versions
alembic revision --message="Init migration" --autogenerate
alembic upgrade head

uvicorn main:app --port=8000 --host='0.0.0.0' --reload



exec "$@"
