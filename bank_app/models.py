# importing the necessary modules 
from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint, json, Markup
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_manager, login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from sqlalchemy import delete, update, text, table
from datetime import date, timedelta
from sqlalchemy.sql import func
from sqlalchemy.orm import class_mapper


# creating a User class 

class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    user_type = db.Column(db.String(50))
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    first_name =  db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(20), nullable=False)
    checking = db.relationship('Checking', backref='users')
    savings = db.relationship('Savings', backref='users')
    credit_card = db.relationship('Credit_Card', backref='users')
    transaction = db.relationship('Transaction', backref='users')
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


# creating a Checking, Savings, and Credit Card model to store the different type of accounts a user can have 
# ADD AN ACCOUNT NUMBER TO THE CHECKING, SAVINGS, AND CREDIT CARD CLASSES

class Checking(db.Model):
    __tablename__ = 'Checking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    balance = db.Column(db.Float, nullable=True)
    transaction = db.relationship('Transaction', backref='checking')
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class Savings(db.Model):
    __tablename__ = 'Savings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    balance = db.Column(db.Float, nullable=True)
    transaction = db.relationship('Transaction', backref='savings')
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class Credit_Card(db.Model):
    __tablename__ = 'Credit_Card'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    balance = db.Column(db.Float, nullable=True)
    transaction = db.relationship('Transaction', backref='credit_card')
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

# Creating a Transactions model where all of the transaction will be stored
# add a user_id checking reference, savings reference number, and credit card reference number
# this will allow the current user to only see their transactions 
class Transaction(db.Model):
    __tablename__ = 'Transactions'
    id = db.Column(db.Integer, primary_key=True)
    checking_id = db.Column(db.Integer, db.ForeignKey('Checking.id'), nullable=True)
    savings_id = db.Column(db.Integer, db.ForeignKey('Savings.id'), nullable=True)
    credit_card_id = db.Column(db.Integer, db.ForeignKey('Credit_Card.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    data = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

