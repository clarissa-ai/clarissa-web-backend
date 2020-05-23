from __future__ import absolute_import

from flask import (
    render_template, 
    redirect, 
    url_for,
    flash
)

from admin import bp 

from flask_login import (
    login_required, 
    current_user, 
    login_user
)

from .forms import LoginForm

from .app.model.user import User

@bp.route('/')
@login_required
def index():
    if not current_user.is_authenticated:
        flash("not authenticated")
    return render_template('dashboard/index.html')



@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
    return render_template('auth/login.html', title="Admin Login", form=login_form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))