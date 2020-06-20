pipenv lock -r > requirements.txt 
pip install -r requirements.txt
python manage.py db upgrade
