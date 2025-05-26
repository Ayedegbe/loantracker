from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Float, DateTime, ForeignKey
from datetime import datetime

db = SQLAlchemy()

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    original_amount = db.Column(db.Float)  # total amount borrowed
    amount = db.Column(db.Float)           # current amount left to pay
    amount_paid = db.Column(db.Float, default=0.0)
    amount_left = db.Column(db.Float, nullable=False, default=0.0)
    last_payment_date = db.Column(DateTime)
    last_payment_amount = db.Column(db.Float, default=0.0)
    registered_date = db.Column(DateTime)
    due = db.Column(DateTime)
    interest = db.Column(db.Float)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    duration = db.Column(db.Integer)
    status = db.Column(db.String(50), default='Pending')
    account_number = db.Column(db.String(20), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    payments = db.relationship('Payment', backref='loan', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    account_number = db.Column(db.String(50))
    date = db.Column(DateTime, default=datetime.now)
    name = db.Column(db.String(50))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
