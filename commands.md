pip freeze > requirements.txt
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
