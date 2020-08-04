from flask import Flask
from celery import Celery
from .config import config_by_name
# python library imports
import requests
import os
import datetime
import json
# Database imports
from app.main.model.illness import Illness, Symptom, Diagnosis
from app.main.model.user import User
from . import db
# Function imports
from app.main.service.illness_service import perform_diagnosis


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def init_celery(app):
    app.config.update(
        CELERY_BROKER_URL='redis://localhost:6379',
        CELERY_RESULT_BACKEND='redis://localhost:6379'
    )
    celery= make_celery(app)

    @celery.task()
    def perform_diagnosis_task(user, user_id, active_illness):
        perform_diagnosis(user, user_id, active_illness)
            