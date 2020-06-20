import os
from .model.user import AdminUser


def root_user_setup(db, curr_env):
    if curr_env == "DEV":
        admin_user = os.getenv("DEV_ADMIN_USER")
        admin_pwd = os.getenv("DEV_ADMIN_PWD")
    elif curr_env == "PRODUCTION":
        admin_user = os.getenv("ADMIN_USER")
        admin_pwd = os.getenv("ADMIN_PWD")
    if not admin_user or not admin_pwd:
        return
    a = AdminUser.query.filter_by(email=admin_user).first()
    if not a:
        a = AdminUser(
            username="Clarissa Root Admin",
            email=admin_user,
            password=admin_pwd
        )
    else:
        a.password = admin_pwd
    db.session.add(a)
    db.session.commit()