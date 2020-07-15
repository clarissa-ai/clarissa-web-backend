FROM python:3.7-slim

WORKDIR /project

ADD . /project

RUN apt-get update -y && apt-get install -y gcc

RUN apt-get install -y build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

RUN pip install pipenv

RUN pipenv install

CMD pipenv run python manage.py db upgrade

EXPOSE 5000

CMD pipenv run python manage.py run
