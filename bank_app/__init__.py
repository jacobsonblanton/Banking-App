# importing the necessary modules
from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from os import path

# naming and initializing the sqlite database
DB_NAME = "database.db"
db = SQLAlchemy()

def create_app():
    # initializing the app and configuring the sqlite databse. Then initializing the sqlachemy into the 
    # database within the Flask app (for mapping purposes)
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'jsbkjbdskjf skfbskfbskjo'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    
    from .views import views 
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # importing the User class from the models file so it can be updated in the database
    from .models import User, Credit_Card, Checking, Savings, Transaction

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# creating the method for the database 
def create_database(app):
    # use this statement below if there is an error running the code, so that everything can have access to the current app
    with app.app_context():
        if not path.exists('bank_app/' + DB_NAME):
            db.create_all()
            print("Database created!")