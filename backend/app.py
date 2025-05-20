from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from models import db, Loan, User
from config import Config
import pandas as pd
import os


app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db.init_app(app)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify({"message": "Login successful"}, 200)
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/loan', methods=['POST'])
def create_loan():
    data = request.json
    loan = Loan(
        name=data['name'],
        amount= data['amount'],
        due=data['due'],
        interest=data['interest'],
        phone=data['phone'],
        email=data['email'],
        duration=data['duration']
    )
    db.session.add(loan)
    db.session.commit()
    return jsonify({'message': 'Loan created successfully'}), 201

@app.route('/api/loans', methods=['GET'])
def get_loans():
    loans = Loan.query.all()
    loan_list = [
        {
            'id': loan.id,
            'name': loan.name,
            'amount': loan.amount,
            'due': loan.due,
            'interest': loan.interest,
            'phone': loan.phone,
            'email': loan.email,
            'duration': loan.duration,
            'status': loan.status
        } for loan in loans
    ]
    return jsonify(loan_list), 200

@app.route('/api/export', methods=['GET'])
def export_loans():
    file_path = os.path.join(os.getcwd(), 'loan_export.csv')
    loans = Loan.query.all()
    loan_list = [{
        'Name': loan.name,
        'Amount': loan.amount,
        'Due Date': loan.due,
        'Interest': loan.interest,
        'Phone': loan.phone,
        'Email': loan.email,
        'Duration': loan.duration,
        'Status': loan.status
    } for loan in loans]

    df = pd.DataFrame(loan_list)
    df.to_csv(file_path, index=False)
    return send_file(file_path, as_attachment=True)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    loans = Loan.query.all()
    now = datetime.now()
    in_seven_days = now + timedelta(days=7)
    total_clients = len(loans)
    active_loans = sum(1 for loan in loans if loan.status == 'Pending')
    upcoming_due = sum(1 for loan in loans if now < datetime.strptime(loan.due, '%Y-%m-%d') <= in_seven_days)
    overdue_loans = sum(1 for loan in loans if datetime.strptime(loan.due, '%Y-%m-%d') < in_seven_days and loan.status == 'Pending')
    total_loaned = sum(float(loan.amount) for loan in loans)

    return jsonify({
        'totalClients': total_clients,
        'activeLoans': active_loans,
        'upcomingDue': upcoming_due,
        'overdue': overdue_loans,
        'totalAmount': total_loaned
    })


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')

    if not username or not password or not name or not phone:
        return jsonify({'message': 'All fields are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409

    user = User(username=username, name=name, phone=phone, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Account created successfully'}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # creates loans.db if not exists
    app.run(debug=True)
 