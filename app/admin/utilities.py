from psutil import (
    cpu_percent,
    virtual_memory,
    disk_usage,
)
from flask import (
    redirect,
    url_for,
    flash
)
from functools import wraps
from flask_login import current_user


def get_system_stats():
    ret = {}
    ret['cpu_percent'] = cpu_percent()
    ret['mem_percent'] = virtual_memory().percent
    ret['disk_percent'] = disk_usage('/').percent
    return ret


def role_required(role):
    def decorator_role_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            role_matched = current_user.role == role
            if not role_matched:
                flash("Failed to verify user permissions for this feature")
                return redirect(url_for('admin.index'))
            return f(*args, **kwargs)
        return decorated
    return decorator_role_required
