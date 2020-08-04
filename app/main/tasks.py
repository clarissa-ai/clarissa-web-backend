from celery import Celery
from flask import Flask
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

app = Flask(__name__)

celery = Celery(app.name, 
            backend='redis://localhost:6379',
            broker='redis://localhost:6379')

@celery.task()
def perform_diagnosis_task(user, user_id, active_illness):
    perform_diagnosis(user, user_id, active_illness)

