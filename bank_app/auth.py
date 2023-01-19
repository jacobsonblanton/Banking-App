# importing the necessary modules 
from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_manager, login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Checking, Savings, Credit_Card, Transaction

auth = Blueprint('auth', __name__)

# acessing the login page
@auth.route('/login', methods=['POST', 'GET'])
def login():
    # getting the email and password of the currrent user from the database
    if request.method == 'POST':
        email = request.form.get('email-content')
        password = request.form.get('password-content')
        # querying and filtering the user database by the first in the "email row" of the user database 
        user = User.query.filter_by(email=email).first()
        # logging in the user if the email and password match
        # redirecting the user if the email and/or password are incorrect, prompting re-entry
        if user:
            if check_password_hash(user.password, password):
                flash("You have successfully logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Password entered is incorrect.", category='error')
                return redirect(url_for('auth.login'))
        # flashing an error message if the email is not found in the database
        else:
            flash("Could not find that email. Make sure the email is entered correctly.", category='error')
            return redirect(url_for('auth.login'))
    #  rendering the login page if the request is not a POST (GET) with the current user that is logged in
    else:
        return render_template("login.html", user=current_user)

# accessing the sign up page
@auth.route('/sign-up', methods=['POST','GET'])
def sign_up():
    # if the user request is a POST request then the following data will be saved to the database 
    if request.method == 'POST':
        type_of_user = request.form.get('user-type-content')
        email = request.form.get('email-content')
        password = request.form.get('password-content')
        first_name = request.form.get('first-name-content')
        last_name = request.form.get('last-name-content')
        address = request.form.get('street-address-content')
        phone = request.form.get('phone-number-content')
        # filtering the database by email and checking if the email entered matches another in the database.
        # Then adding the user's info if the email is not already in the database
        print(password)
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
            return redirect(url_for('auth.sign_up'))
        elif len(email) < 4:
            flash('Email must have at least 4 characters.', category='error')
            return redirect(url_for('auth.sign_up'))
        elif len(first_name) < 2:
            flash('First name must have at least 2 characters.', category='error')
            return redirect(url_for('auth.sign_up'))
        elif len(last_name) < 2:
            flash('Last name must have at least 2 characters.', category='error')
            return redirect(url_for('auth.sign_up'))
        else:
            new_user = User(user_type=type_of_user, email=email, first_name=first_name, last_name=last_name,
                             password=generate_password_hash(password, method='sha256'), phone=phone, address=address)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
    # rendering the sign up page if the request is a 'POST' request with the current user that is logged in
    else:
        return render_template("sign_up.html", user=current_user)
    
# logging user out and redirecting to login page
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))