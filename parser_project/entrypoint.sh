#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python ./parser_project/manage.py makemigrations
python ./parser_project/manage.py migrate
python ./parser_project/manage.py createcachetable
docker run liiight/notifiers
#python ./parser_project/manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')"
exec "$@"

