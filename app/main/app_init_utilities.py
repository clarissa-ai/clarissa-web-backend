import os
from .model.user import AdminUser
import datetime


def root_user_setup(db, curr_env):
    if curr_env == "DEV":
        admin_user = os.getenv("DEV_ADMIN_USER")
        admin_pwd = os.getenv("DEV_ADMIN_PWD")
    elif curr_env == "PRODUCTION":
        admin_user = os.getenv("ADMIN_USER")
        admin_pwd = os.getenv("ADMIN_PWD")
    if not admin_user or not admin_pwd:
        return
    try:
        a = AdminUser.query.filter_by(email=admin_user).first()
        if not a:
            a = AdminUser(
                username="Clarissa Root Admin",
                email=admin_user,
                password=admin_pwd,
                registered_on=datetime.datetime.utcnow()
            )
        else:
            a.password = admin_pwd
        db.session.add(a)
        db.session.commit()
    except Exception as e:
        print('Failed root_user_setup')
        print(e)
