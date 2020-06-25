FROM python:3.7-slim

WORKDIR /project

ADD . /project

RUN apt-get update -y && apt-get install -y gcc

RUN pip install pipenv

RUN pipenv install

CMD pipenv run python manage.py db upgrade

CMD pipenv run python manage.py run