# importing the necessary modules 
from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint, json, Markup
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_manager, login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Checking, Savings, Credit_Card, Transaction
from .auth import sign_up
from sqlalchemy import delete, update, text, insert, join
from datetime import date, timedelta
from sqlalchemy.sql import func
import itertools

views = Blueprint('views', __name__)

@views.route('/', methods=['POST', 'GET'])
@login_required
def home():

    # display all user information in a visually plaesing way
    # give the user to the option to add funds/make deposit on this page (If the user adds funds or makes a deposit,
    # add this to the transacions table) and redirect to add_funds page
    checking = db.session.query(Checking).all()
    savings = db.session.query(Savings).all()
    transactions = db.session.query(Transaction).all()
    credit_card = db.session.query(Credit_Card).all()

    return render_template("home.html",user=current_user, checking=checking, savings=savings, credit_card=credit_card,
                            transactions=transactions)

@views.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():

    # display all the user information on this page, give the user options to change fields, such as email and password
    users = db.session.query(User).all()

    return render_template("profile.html", user=current_user, users=users)

@views.route('/transactions', methods=['POST', 'GET'])
@login_required
def transaction():
    # getting all the transactions and rendering them on the transactions page
    transactions = db.session.query(Transaction).all()
    
    # add a transaction variable to each method. Before committing to the session to the database, add the transaction to the 
    # Transactions table. Reference where the Transaction came from using the user_id and account_id
    
    #print(transactions_result)

    return render_template("transactions.html", user=current_user, transactions=transactions)
  
@views.route('/add-account', methods=['POST', 'GET'])
@login_required
def add_account():
    if request.method == 'POST':
        acct_type = request.form.get('account-content')
        if acct_type == 'checking':
            db.session.add(Checking(balance=0.00, user_id=current_user.id))
            db.session.commit()
            flash('Checking Account added', category='success')
            return redirect(url_for('views.home'))
        elif acct_type == 'savings':
            db.session.add(Savings(balance=0.00, user_id=current_user.id))
            db.session.commit()
            flash('Savings Account added', category='success')
            return redirect(url_for('views.home'))
        else:
            db.session.add(Credit_Card(balance=0.00, user_id=current_user.id))
            db.session.commit()
            flash('Crdit Card Account added', category='success')
            return redirect(url_for('views.home'))

    return render_template("add_account.html",user=current_user)
    
@views.route('/check-balances', methods=['POST', 'GET'])
@login_required
def check_balance():
    # display all user account balances on this page
    # getting all the accounts in the checking table
    checking = db.session.query(Checking).all()
    savings = db.session.query(Savings).all()
    credit_card = db.session.query(Credit_Card).all()

    return render_template("check_balance.html", user=current_user, checking=checking, savings=savings, 
    credit_card=credit_card)

@views.route('/make-payment', methods=['POST', 'GET'])
@login_required
def make_payment():
    
    # prompt user to make a payment, ask what account they would like to make a payment from
    # check that account balance, if the user has sufficient funds, initiate that payment.
    # (will update this payment to the transactions table)

    # getting the checking accounts where the user_id is the same as the current user id
    checking = text('SELECT id,balance FROM Checking WHERE checking.user_id == :user')
    checking_result = db.engine.execute(checking, user = current_user.id).fetchall()
    checking_data = dict(checking_result)
    # getting the savings accounts where the user_id is the same as the current user id
    savings = text('SELECT id,balance FROM Savings WHERE savings.user_id == :user')
    savings_result = db.engine.execute(savings, user = current_user.id).fetchall()
    savings_data = dict(savings_result)
    # getting the credit car accounts where the user_id is the same as the current user id
    credit_card = text('SELECT id,balance FROM Credit_Card WHERE credit_card.user_id == :user')
    credit_card_result = db.engine.execute(credit_card, user = current_user.id).fetchall()
    credit_card_data = dict(credit_card_result)
    if request.method == 'POST':
        acct_payment_from = request.form.get('payment-from-type-content')
        payment_from = int(request.form.get('payment-from-content'))
        credit_card_number = int(request.form.get('credit-card-account-content'))
        payment_amount = float(request.form.get('payment-amount-content'))
        if acct_payment_from == 'Checking': # checking if the account selected is checking
            for key in checking_data: # looping the checking data to see the checking number is in the dict
                if payment_from == key:
                    checking_balance = checking_data[key] # setting the balance associated with the checking number to a variable
                    if checking_balance >= payment_amount: # checking if the balance from the checking account selected is greater than or equal to the payment amount
                        new_checking_balance = checking_balance-payment_amount # updating the new checking balance amount 
                        payment_from_checking = db.session.query(Checking).get(key)
                        payment_from_checking.balance = new_checking_balance # updating the checking amount to the balance column in the checking table
                        for key_2 in credit_card_data: # loop through the credit card data to see if there is a credit card number equal to user inputed number
                            if credit_card_number == key_2: # if there is a credit card number associated with the user inputed nuber the following will be executed
                                credit_card_balance = credit_card_data[key_2]
                                new_credit_card_balance = credit_card_balance-payment_amount # setting the balance associated with that number equal to a variable
                                credit_card_number_one = db.session.query(Credit_Card).get(key_2)
                                credit_card_number_one.balance = new_credit_card_balance # updating the credit card balance in the credit card table
                                transaction = Transaction(user_id=current_user.id, credit_card_id=credit_card_number_one, checking_id=payment_from.id, data=str(payment_amount)+' payment to credit card account '+str(credit_card_number)+' from checking account '+str(payment_from, amount=payment_amount)) # adding the transaction to the Transaction table in the database
                                db.session.add(transaction)
                                db.session.commit() # committing the changes to the database
                            flash('Payment has been made from Checking Account!', category='success')
                            return redirect(url_for('views.home'))
                        flash('We cannot find a Credit Card associated with that number', category='error')
                        return redirect(url_for('views.make_payment'))
                    else:
                        flash('This account has insufficient funds for this payment amount', category='error')
                        return redirect(url_for("view.make_payment"))
                flash('We cannt find a Checking Account with that reference nuber', category='error')
                return redirect(url_for("views.make_payment"))
                    
        if acct_payment_from == 'Savings': # checking if the account selected is savings
            for key in savings_data: # looping the savings data to see the checking number is in the dict
                if payment_from == key:
                    savings_balance = savings_data[key] # setting the balance associated with the savings number to a variable
                    if savings_balance >= payment_amount: # checking if the balance from the savings account selected is greater than or equal to the payment amount
                        new_savings_balance = savings_balance-payment_amount # updating the new savings balance amount 
                        payment_from = db.session.query(Checking).get(key)
                        payment_from.balance = new_savings_balance # updating the savings amount to the balance column in the savings table
                        for key_2 in credit_card_data: # loop through the credit card data to see if there is a credit card number equal to user inputed number
                            if credit_card_number == key_2: # if there is a credit card number associated with the user inputed nuber the following will be executed
                                credit_card_balance = credit_card_data[key_2]
                                new_credit_card_balance = credit_card_balance-payment_amount # setting the balance associated with that number equal to a variable
                                credit_card_number_one = db.session.query(Credit_Card).get(key_2)
                                credit_card_number_one.balance = new_credit_card_balance # updating the credit card balance in the credit card table
                                transaction = Transaction(user_id=current_user.id, savings_id=payment_from.id, credit_card_id=credit_card_number_one.id, data=str(payment_amount)+' payment to credit card account '+str(credit_card_number)+' from checking account '+str(payment_from, amount=payment_amount)) # adding the transaction to the Transaction table in the database
                                db.session.add(transaction)
                                db.session.commit() # committing the changes to the database
                            flash('Payment has been made from Savings Account!', category='success')
                            return redirect(url_for('views.home'))
                        flash('We cannot find a Credit Card associated with that number', category='error')
                        return redirect(url_for('views.make_payment'))
                    else:
                        flash('This account has insufficient funds for this payment amount', category='error')
                        return redirect(url_for("view.make_payment"))
                flash('We cannt find a Savings Account with that reference nuber', category='error')
                return redirect(url_for("views.make_payment"))


    return render_template("make_payment.html",user=current_user)

@views.route('/transfer-funds', methods=['POST', 'GET'])
@login_required
def transfer_funds():
    # getting the checking accounts where the user_id is the same as the current user id
    checking = text('SELECT id,balance FROM Checking WHERE checking.user_id == :user')
    checking_result = db.engine.execute(checking, user = current_user.id).fetchall()
    checking_data = dict(checking_result)
    # getting the savings accounts where the user_id is the same as the current user id
    savings = text('SELECT id,balance FROM Savings WHERE savings.user_id == :user')
    savings_result = db.engine.execute(savings, user = current_user.id).fetchall()
    savings_data = dict(savings_result)
    if request.method == 'POST':
        acct_transfer_funds_from = request.form.get('transfer-from-type-content')
        acct_transfer_funds_to = request.form.get('transfer-to-type-content')
        transfer_funds_from = int(request.form.get('transfer-from-content'))
        transfer_funds_to = int(request.form.get('transfer-to-content'))
        transfer_amount = float(request.form.get('transfer-amount-content'))
        # this is the process for the user if they want to transfer funds from Checking-Checking or CHecking-Savings
        if acct_transfer_funds_from == 'Checking'.lower():
            for key in checking_data:
                if transfer_funds_from == key: # comparing the account id number to the key
                    balance = checking_data[key] # balance equals the value of the key 
                    if balance >= transfer_amount: # checking if the current balance is gretater than or equal to the transfer amount
                        new_balance = balance-transfer_amount # the new balance is equal to the current balance-transfer amount added
                        checking_transfer_funds_from = db.session.query(Checking).get(key) # querying the account by the account id/key
                        checking_transfer_funds_from.balance = new_balance # updating the account balance with the new balance
                        # going through the same series of checks for the right account number and add the amount to 
                        # the correct account whether that be checking or savings
                        
                        if acct_transfer_funds_to == 'Checking'.lower():
                            for key_2 in checking_data:
                                if transfer_funds_to == key_2:
                                    balance_2 = checking_data[key_2]
                                    new_balance_transfer_to = balance_2+transfer_amount # the new balance for the transfer amount is the current balance+transfer amount  
                                    checking_transfer_funds_to = db.session.query(Checking).get(key_2)
                                    checking_transfer_funds_to.balance = new_balance_transfer_to
                                    transaction = Transaction(user_id=current_user.id, checking_id=acct_transfer_funds_from.id, data=str(transfer_amount)+' added to checking '+str(transfer_funds_to)+' from checking account '+str(transfer_funds_from, amount=transfer_amount)) # adding the transaction to the Transaction table in the database
                                    db.session.add(transaction)
                                    db.session.commit() # committing the changes to the database
                                    flash('Amount transferred into Checking account!', category='success')
                                    return redirect(url_for("views.home"))
                            flash('We cannot find a Checking account with that refernce number to transfer funds to', category='error')
                            return redirect(url_for("views.transfer_funds"))
                        if acct_transfer_funds_to == 'Savings'.lower():
                            for key_2 in savings_data:
                                if transfer_funds_to == key_2:
                                    balance_2 = savings_data[key_2]
                                    new_balance_transfer_to = balance_2+transfer_amount # the new balance for the transfer amount is the current balance+transfer amount  
                                    savings_transfer_funds_to = db.session.query(Savings).get(key_2)
                                    savings_transfer_funds_to.balance = new_balance_transfer_to
                                    transaction = Transaction(user_id=current_user.id, checking_id=acct_transfer_funds_from.id, data=str(transfer_amount)+' added to savings '+str(transfer_funds_to)+' from checking account '+str(transfer_funds_from), amount=transfer_amount) # adding the transaction to the Transaction table in the database
                                    db.session.add(transaction)
                                    db.session.commit() # committing the changes to the database
                                    flash('Amount trasnsferred into Savings account!', category='success')
                                    return redirect(url_for("views.home"))
                            flash('We cannot find a Savings account with that refernce number to transfer funds to', category='error')
                            return redirect(url_for("views.transfer_funds"))
                    else:
                        flash('This account has insufficient funds for the amount requested to transfer', category='error')

        # this is the process for the user if they want to transfer funds from Savings-Checking or Savings-Savings
        if acct_transfer_funds_from == 'Savings'.lower():
            for key in savings_data:
                if transfer_funds_from == key: # comparing the account id number to the key
                    balance = savings_data[key] # balance equals the value of the key 
                    if balance >= transfer_amount: # checking if the current balance is gretater than or equal to the transfer amount
                        new_balance = balance-transfer_amount # the new balance is equal to the current balance-transfer amount added
                        savings_transfer_funds_from = db.session.query(Savings).get(key) # querying the account by the account id/key
                        savings_transfer_funds_from.balance = new_balance # updating the account balance with the new balance
                        # going through the same series of checks for the right account number and add the amount to 
                        # the correct account whether that be checking or savings
                        
                        if acct_transfer_funds_to == 'Checking'.lower():
                            for key_2 in checking_data:
                                print(transfer_funds_to)
                                if transfer_funds_to == key_2:
                                    balance_2 = checking_data[key_2]
                                    new_balance_transfer_to = balance_2+transfer_amount # the new balance for the transfer amount is the current balance+transfer amount  
                                    checking_transfer_funds_to = db.session.query(Checking).get(key_2)
                                    checking_transfer_funds_to.balance = new_balance_transfer_to
                                    transaction = Transaction(user_id=current_user.id, savings_id=acct_transfer_funds_from.id, data=str(transfer_amount)+' added to checking '+str(transfer_funds_to)+' from savings account '+str(transfer_funds_from), amount=transfer_amount) # adding the transaction to the Transaction table in the database
                                    db.session.add(transaction)
                                    db.session.commit() # committing the changes to the database
                                    flash('Amount transferred into Checking account!', category='success')
                                    return redirect(url_for("views.home"))
                            flash('We cannot find a Checking account with that refernce number to transfer funds to', category='error')
                            return redirect(url_for("views.transfer_funds"))
                        if acct_transfer_funds_to == 'Savings'.lower():
                            for key_2 in savings_data:
                                balance_2 = savings_data[key_2]
                                if transfer_funds_to == key_2:
                                    new_balance_transfer_to = balance_2+transfer_amount # the new balance for the transfer amount is the current balance+transfer amount  
                                    savings_transfer_funds_to = db.session.query(Savings).get(key_2)
                                    savings_transfer_funds_to.balance = new_balance_transfer_to
                                    transaction = Transaction(user_id=current_user.id, savings_id=acct_transfer_funds_from.id, data=str(transfer_amount)+' added to savings '+str(transfer_funds_to)+' from savings account '+str(transfer_funds_from), amount=transfer_amount) # adding the transaction to the Transaction table in the database
                                    db.session.add(transaction)
                                    db.session.commit() # committing the changes to the database
                                    flash('Amount trasnsferred into Savings account!', category='success')
                                    return redirect(url_for("views.home"))
                            flash('We cannot find a Savings account with that refernce number to transfer funds to', category='error')
                            return redirect(url_for("views.transfer_funds"))
                    else:
                        flash('This account has insufficient funds for the amount requested to transfer', category='error')
            flash('We cannot find a Checking account with that reference number.', category='error')
            return redirect(url_for("views.transfer_funds"))

        
    # prompt the user to transfer funds, ask what account they would like to transfer from,
    # check that account balance, if they have insufficient funds, prompt the to add funds, if they choose yes,
    # redirect them to the add_funds page to add funds. Update this to the transactions table
    
    return render_template("transfer_funds.html",user=current_user, checking=checking, savings=savings)

@views.route('/add-funds', methods=['POST', 'GET'])
@login_required
def add_funds():
    
    # getting the checking accounts where the user_id is the same as the current user id
    checking = text('SELECT id,balance FROM Checking WHERE checking.user_id == :user')
    checking_result = db.engine.execute(checking, user = current_user.id).fetchall()
    data = dict(checking_result)
    # getting the savings accounts where the user_id is the same as the current user id
    savings = text('SELECT id,balance FROM Savings WHERE savings.user_id == :user')
    savings_result = db.engine.execute(savings, user = current_user.id).fetchall()
    savings_data = dict(savings_result)
    if request.method == 'POST':
        # getting the amount the user would like to add and which account to add to
        account_type = request.form.get('account-type-content')
        account = int(request.form.get('add-to-content'))
        amount =  float(request.form.get('amount-content'))
        if account_type == 'Checking'.lower():
            for key in data:
                if account == key: # comparing the account id number to the key
                    balance = data[key] # balance equals the value of the key 
                    new_balance = balance+amount # the new balance is equal to the current balance+amount added
                    checking_account = db.session.query(Checking).get(key) # querying the account by the account id/key
                    checking_account.balance = new_balance # updating the account balance with the new balance
                    transaction = Transaction(user_id=current_user.id, checking_id=checking_account.id, data=str(amount)+' added to checking '+str(account)+' account', amount=amount) # adding the transaction to the Transaction table in the database
                    db.session.add(transaction)
                    db.session.commit() # committing the changes to the database
                    flash('Amount added into Checking account!', category='success')
                    return redirect(url_for("views.home"))
                flash('We cannot find a Checking account with that reference number.', category='error')
                return redirect(url_for("views.add_funds"))
        if account_type == 'Savings'.lower():
            for key in savings_data:
                if account == key: # comparing the account id number to the key
                    balance = savings_data[key] # balance equals the value of the key 
                    new_balance = balance+amount # the new balance is equal to the current balance+amount added
                    account = db.session.query(Savings).get(key) # querying the account by the account id/key
                    account.balance = new_balance # updating the account balance with the new balance
                    transaction = Transaction(user_id=current_user.id, savings_id=account.id, data=str(amount)+' added to savings account', amount=amount) # adding the transaction to the Transaction table in the database
                    db.session.add(transaction)
                    db.session.commit() # committing the changes to the database
                    flash('Amount added into Savings account!', category='success')
                    return redirect(url_for("views.home"))
            flash('We cannot find a Savings account with that reference number.', category='error')
            return redirect(url_for("views.add_funds"))

    return render_template("add_funds.html", user=current_user)