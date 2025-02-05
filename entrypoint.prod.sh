python manage.py collecstatic
python manage.py migrate --noinput
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 SUN.wsgi:application