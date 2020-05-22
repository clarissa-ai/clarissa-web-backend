from app import app
from app import api
from flask import jsonify, render_template
from flask_restful import Resource
from .resources import *
import re

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')




# User authentication endpoints
api.add_resource(UserRegistration, '/api/registration')         # Register a new user
api.add_resource(UserLogin, '/api/login')                       # Login for returning user
api.add_resource(UserLogoutAccess, '/api/logout/access')        # Logout (deactivate access token)
api.add_resource(UserLogoutRefresh, '/api/logout/refresh')      # Logout (deactivate refresh token)
api.add_resource(TokenRefresh, '/api/token/refresh')            # Endpoint to get new access token using refresh token

# Core API Endpoints
api.add_resource(Dashboard, '/api/dashboard')                   # Return all information necessary for main user dashboard
api.add_resource(CreateReport, '/api/create_report')            # Create a new report for a user
api.add_resource(AddSymptom, '/api/add_symptom')                # Add a symptom to an individual report
api.add_resource(GetReport, '/api/get_report')                  # Get all details from a report
api.add_resource(AddComment, '/api/add_comment')                # Add a comment to a report


# Diagnosis related endpoints 
# api.add_resource(DiagnoseReport, '/api/get_diagnosis')          # Get a diagnosis for a report
api.add_resource(GetAPIData, '/api/get_symptom_data')


# API Endpoints for testing only
api.add_resource(AllUsers, '/api/users')                        # Returns a list of all users
api.add_resource(AllReports, '/api/reports')