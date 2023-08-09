#!/bin/sh

if [ "$DATABASE" = "twitter_clone" ]
then
    echo "Waiting for db starting..."

    while ! curl -s $SQL_HOST:$SQL_PORT >/dev/null; do
      sleep 0.5
    done

    echo "PostgreSQL started"
fi

mkdir -p ./alembic/versions
alembic revision --message="Init migration" --autogenerate
alembic upgrade head

uvicorn main:app --port=8000 --host='0.0.0.0' --reload



exec "$@"
