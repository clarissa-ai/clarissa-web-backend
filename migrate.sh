pipenv lock -r > requirements.txt 
python -m pip install -r requirements.txt
python manage.py db upgrade