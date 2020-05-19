from flask_restful import Resource, reqparse
from app import api
from .models import User, Report, Symptom, Comment
from app import db
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from datetime import datetime, timedelta, date
from random import choice
import os
import re

#---------------------------------------------------#
# START OF SECTION OF POST REQUEST ARGUMENT PARSERS #
#---------------------------------------------------#

# parser for authenticating
auth_parser = reqparse.RequestParser()
auth_parser.add_argument('email', help = 'This field cannot be blank', required = True)
auth_parser.add_argument('password', help = 'This field cannot be blank', required = True)

# parser for registration
registration_parser = reqparse.RequestParser()
registration_parser.add_argument('first_name', help = 'This field cannot be blank', required = True)
registration_parser.add_argument('age', type=int, help = 'This field cannot be blank', required = True)
registration_parser.add_argument('email', help = 'This field cannot be blank', required = True)
registration_parser.add_argument('password', help = 'This field cannot be blank', required = True)

# parser for adding a new report
report_parser = reqparse.RequestParser()
report_parser.add_argument('title', help = 'This field cannot be blank', required = True)
report_parser.add_argument('symptoms')
report_parser.add_argument('comment')

# parser for getting a report
get_report_parser = reqparse.RequestParser()
get_report_parser.add_argument('id', help = 'This field cannot be blank', required = True)

# parser for adding a new symptom to a report
symptom_parser = reqparse.RequestParser()
symptom_parser.add_argument('report_id', help = 'This field cannot be blank', required = True)
symptom_parser.add_argument('name', help = 'This field cannot be blank', required = True)
symptom_parser.add_argument('api_id', type=int, help = 'This field cannot be blank', required = True)
symptom_parser.add_argument('severity', type=int, help = 'This field cannot be blank', required = True)
symptom_parser.add_argument('data', help = 'This field cannot be blank', required = True)

# parser for adding a comment to a report
comment_parser = reqparse.RequestParser()
comment_parser.add_argument('report_id', type=int, help = 'This field cannot be blank', required = True)
comment_parser.add_argument('text', help = 'This field cannot be blank', required = True)

#---------------------------#
# END OF ARG PARSER SECTION #
#---------------------------#



#----------------------------#
# RESOURCES FOR TESTING ONLY #
#----------------------------#
class AllUsers(Resource):
    def get(self):
        return User.return_all()
    
    def delete(self):
        return User.delete_all()

class AllReports(Resource):
    def get(self):
        return Report.return_all()

    def delete(self):
        return Report.delete_all()

#--------------------------#
# END OF TESTING ENDPOINTS #
#--------------------------#



#------------------------------------------------#
# START OF SECTION FOR USER AUTHENTICATION LOGIC #
#------------------------------------------------#
class UserRegistration(Resource):
    def post(self):
        data = registration_parser.parse_args()
        new_user = User(
            first_name = data['first_name'],
            age = data['age'],
            email = data['email'].lower(),
            password = User.generate_hash(data['password'])
        )

        if User.find_by_email(data['email'].lower()):
            return {
                'message': 'User {} already exists'. format(data['email'].lower()),
                'status': False
            }
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity = data['email'].lower())
            refresh_token = create_refresh_token(identity = data['email'].lower())
            return {
                'message': 'User has been registered: {}'.format(new_user.email),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'status': True
            }
        except:
            return {
                'message': 'Error while attempting to register user.',
                'status': False
            }, 500


class UserLogin(Resource):
    def post(self):
        data = auth_parser.parse_args()
        current_user = User.find_by_email(data['email'].lower())

        if not current_user:
            return {
                'message': 'User {} doesn\'t exist'.format(data['email'].lower()),
                'status': False
            }
        
        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity = data['email'].lower())
            refresh_token = create_refresh_token(identity = data['email'].lower())
            return {
                'message': 'Logged in as {}'.format(current_user.email),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'status': True
            }
        else:
            return {
                'message': 'Wrong credentials',
                'status': False
            }
      
      
class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {
                'message': 'Access token has been revoked',
                'status': True
            }
        except:
            return {
                'message': 'Something went wrong',
                'status': False
            }, 500
      
      
class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {
                'message': 'Refresh token has been revoked',
                'status': True
            }
        except:
            return {
                'message': 'Something went wrong',
                'status': False
            }, 500
      
      
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {
            'access_token': access_token,
            'status': True
        }
      
#--------------------------------------#
# END OF USER AUTHENTICATION ENDPOINTS #
#--------------------------------------#


#------------------------#
# REGULAR DATA RESOURCES # 
#------------------------#

class Dashboard(Resource):
    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user).first()
        return {
            'current_user': {
                'id': current_user.id,
                'first_name': current_user.first_name,
                'age': current_user.age,
                'email': current_user.email,
                'symptom_count': len(current_user.symptoms),
                'report_count': len(current_user.reports)
            },
            'reports': [{'title': r.title} for r in current_user.reports],
            'symptoms': [{} for s in current_user.symptoms],
        }


class CreateReport(Resource):
    @jwt_required
    def post(self):
        # Get current user's email from jwt token and pull from database
        current_user = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user).first()

        # Grab passed in parameters and generate report
        data = report_parser.parse_args()
        new_report = Report(
            title = data['title'],
            user_id = current_user.id,
            date = datetime.now().date()
        )
        try:
            new_report.save_to_db()

            if data['comment']:
                c = Comment(
                    text = data['comment'], 
                    report_id = new_report.id
                )
                comment.save_to_db()

            return {
                'message': 'Successfully added report "{}" to database.'.format(new_report.title),
                'status': True
            }
        except Exception as e:
            print(e)
            return {
                'message': 'Failed to add report to database.',
                'status': False
            }

class GetReport(Resource):
    @jwt_required
    def get(self):
        # Get current user's email from jwt token and pull from database
        current_user = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user).first()
        
        data = get_report_parser.parse_args()

        r = Report.query.filter_by(id=int(data['id'])).first()
        if r.user_id != current_user.id:
            print()
            return {
                'message': 'User does not have permission to access this report.',
                'status': False
            }
        return {
            'report': {
                'title': r.title,
                'date': r.date.strftime("%m/%d/%Y, %H:%M:%S"),
                'symptoms': [{'name': s.name, 'severity': s.severity, 'data': s.data, 'api_id': s.api_id} for s in r.symptoms],
                'comments': [{'text': c.text, 'datetime': c.datetime.strftime("%m/%d/%Y, %H:%M:%S")} for c in r.comments]
            },
            'message': 'Successfully retrieved report.',
            'status': True
        }

class AddSymptom(Resource):
    @jwt_required
    def post(self):
        current_user = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user).first()

        data = symptom_parser.parse_args()

        if Report.query.filter_by(id=data['report_id']).first() not in current_user.reports:
            return {
                'message': 'User not authorized to modify this report.',
                'status': False
            }

        new_symptom = Symptom(
            name = data['name'],
            api_id = data['api_id'],
            severity = data['severity'],
            data = data['data'],
            report_id = data['report_id'],
            datetime = datetime.now()
        )
        try:
            db.session.add(new_symptom)
            db.session.commit()
            return {
                'message': 'Successfully added symptom {} to database.'.format(new_symptom.name),
                'status': True
            }
        except:
            return {
                'message': 'Failed to add symptom to database.',
                'status': False
            }

class AddComment(Resource):
    @jwt_required
    def post(self):
        current_user = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user).first()

        data = comment_parser.parse_args()

        if Report.query.filter_by(id=data['report_id']).first().user_id != current_user.id:
            return {
                'message': "User is not authorized to add comment to this report.",
                'status': False
            }

        c = Comment(
            report_id = data['report_id'],
            text =  data['text'],
            datetime = datetime.now()
        )

        try:
            c.save_to_db()
            return {
                'message': "Comment successfully added to report.",
                'status': True
            }
        except:
            return {
                'message': 'Failed to add comment to report.',
                'status': False
            }




class DiagnoseReport(Resource):
    @jwt_required
    def post(self):
        # Get current user's email from jwt token and pull from database
        current_user = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user).first()
        
        data = diagnosis_parser.parse_args()
        report_id = int(data['report_id'])
        r = Report.find_by_id(report_id)
        
        if r.user_id != current_user.id:
            return {
                'message': 'User is not authorized to diagnose this report',
                'status': False
            }
        
import json
class GetAPIData(Resource):
    def get(self):
        path = '/home/coder/CratesMed/server/app/apimedic/data/04-22-2020.15-04-46_APIsave.json'
        with open(path, 'r') as f:
            return json.load(f)
        

#------------------------------------#
# REGULAR DATA RESOURCES SECTION END # 
#------------------------------------#
