from passlib.hash import argon2
from passlib.apps import custom_app_context as pwd_context
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated=["auto"])

auth = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
 
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and pwd_context.verify(password, user.password):  # Use verify for Passlib
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash('Incorrect email or password, try again.', category='error')

    return render_template('login.html', user=current_user, form=form)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 9:
            flash('Email must be greater than 9 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 8 characters.', category='error')
        else:
            hashed_password = argon2.hash(password1)
            new_user = User(email=email, first_name=first_name, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))