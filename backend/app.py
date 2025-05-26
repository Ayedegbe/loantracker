from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file
from sqlalchemy import or_
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, Loan, User, Payment
from config import Config
import pandas as pd
import os



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

jwt = JWTManager(app)
app.config.from_object(Config)
db.init_app(app)
CORS(app)
print("Using database at:", app.config['SQLALCHEMY_DATABASE_URI'])

with app.app_context():
    db.create_all()  # creates loans.db if not exists

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    identifier = data.get('identifier')
    password = data.get('password')
    if not identifier or not password:
        return jsonify({'message': 'Username/email and password are required'}), 400

    user = User.query.filter(
        or_(User.username == identifier, User.email == identifier)
    ).first()

    if user and user.check_password(password):
        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": token}), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/loan', methods=['POST'])
@jwt_required()
def create_loan():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.json
    due_date = datetime.now() + timedelta(days=7)
    last_loan = Loan.query.order_by(Loan.id.desc()).first()
    next_account_number = f"ACCT{(last_loan.id + 1) if last_loan else 1:06d}"

    loan = Loan(
        name=data['name'],
        original_amount=data['amount'],     # Original loan amount
        amount=data['amount'],              # Current tracking amount
        amount_left=data['amount'],         # Start with full balance
        amount_paid=0.0,
        last_payment_date=None,
        last_payment_amount=0.0,
        registered_date=datetime.now(),
        due=due_date,
        interest=data['interest'],
        phone=data['phone'],
        email=data['email'],
        duration=data['duration'],
        status=data.get('status', 'Pending'),
        account_number=next_account_number,
                 # Start with empty history
        user_id=user_id
    )
    db.session.add(loan)
    db.session.commit()
    return jsonify({'message': 'Loan created successfully'}), 201

@app.route('/api/loans', methods=['GET'])
@jwt_required()
def get_loans():
    loans = Loan.query.all()
    # loans = Loan.query.filter_by(user_id=user_id).all()

    loan_list = [
        {
            'id': loan.id,
            'name': loan.name,
            'amount': loan.amount,
            'amount_left': loan.amount_left,
            'due': loan.due,
            'interest': loan.interest,
            'phone': loan.phone,
            'email': loan.email,
            'duration': loan.duration,
            'status': loan.status,
            'account_number': loan.account_number,
            'registered_date': loan.registered_date.strftime("%d/%m/%Y")
        } for loan in loans
    ]
    return jsonify(loan_list), 200

@app.route('/api/export', methods=['GET'])
@jwt_required()
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


@app.route('/api/loans/due-soon', methods=['GET'])
@jwt_required()
def get_loans_due_this_week():
    user_id = get_jwt_identity()
    today = datetime.now().date()
    start_date = today + timedelta(days=7)
    end_date = today + timedelta(days=14)

    due_loans = []

    loans = Loan.query.filter_by(user_id=user_id).all()
    for loan in loans:
        try:
            due_date = datetime.strptime(loan.due, "%Y-%m-%d").date()
        except Exception:
            continue  # skip invalid dates
        if loan.last_payment_date:
            next_due_date = loan.last_payment_date.date() + timedelta(days=7)
        elif loan.registered_date:
            next_due_date = loan.registered_date.date() + timedelta(days=7)
        else:
            continue  # skip if no base date

        if start_date < next_due_date <= end_date and loan.amount_left > 0:
            due_loans.append({
                'id': loan.id,
                'name': loan.name,
                'amount': loan.original_amount or loan.amount,
                'amount_left': loan.amount_left,
                'last_payment_amount': loan.last_payment_amount,
                'last_payment_date': loan.last_payment_date.strftime("%Y-%m-%d") if loan.last_payment_date else None,
                'due': loan.due,
                'status': loan.status
            })

    return jsonify(due_loans)

@app.route('/api/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    loans = Loan.query.filter_by(user_id=user_id).all()
  
    total_clients = len(loans)
    active_loans = len([loan for loan in loans if loan.amount_left > 0])
    total_amount = sum(loan.amount_left for loan in loans if loan.original_amount)

    now = datetime.now()
    upcoming_due = 0
    overdue = 0

    for loan in loans:
        if loan.amount_left <= 0:
            continue

        if loan.last_payment_date:
            due_date = loan.last_payment_date
            next_due_date = due_date + timedelta(days=7)
        else:
            due_date = loan.registered_date
            next_due_date = due_date + timedelta(days=7)
            # If no payment has been made, assume the loan started at `due - duration` weeks ago
            # try:
            #     # due_date = datetime.strptime(loan.due, "%Y-%m-%d")
            #     loan_start = due_date - timedelta(weeks=loan.duration)
            #     next_due_date = loan_start + timedelta(days=7)
            # except Exception as e:
            #     continue  # invalid date, skip

        if next_due_date < now:  # overdue
            overdue += 1
        elif now <= next_due_date <= now + timedelta(days=7):  # due this week
            upcoming_due += 1

    return jsonify({
        'totalClients': total_clients,
        'activeLoans': active_loans,
        'upcomingDue': upcoming_due,
        'overdue': overdue,
        'totalAmount': total_amount
    })


@app.route('/api/register', methods=['POST'])
# @jwt_required()
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')

    if not all ([username, password, name, phone, email]):
        return jsonify({'message': 'All fields are required'}), 400

    existing_user = User.query.filter(
        (User.email == email)
    ).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 409

    user = User(username=username, name=name, phone=phone, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Account created successfully'}), 201

@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user:
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'username': user.username
        }), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/api/payment', methods=['POST'])
@jwt_required()
def make_payment():
    data = request.json
    loan_id = data.get('loan_id')
    amount_paid = float(data.get('amount_paid',0))

    # if loan_id is None or payment is None:
    #     return jsonify({'message': 'Missing loan ID or amount'}), 400
    try:
        amount_paid = float(amount_paid)
    except ValueError:
        return jsonify({'message': 'Invalid payment amount'}), 400
    
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    loan.amount_left -= float(amount_paid)
    loan.last_payment_amount = float(amount_paid)
    loan.last_payment_date = datetime.now()
    loan.due = loan.last_payment_date + timedelta(days=7)
    loan.amount_paid += float(amount_paid)
    if loan.amount_left <= 0:
        loan.amount_left = 0
        loan.status = f'Paid: {datetime.now()}'
    
    payment_entry = Payment(
    loan_id=loan.id,
    date=loan.last_payment_date,
    amount=amount_paid,
    name=loan.name,
    account_number=loan.account_number
)
   
        
       
    
    # history = loan.payment_history or []
    # history.append(payment_entry)
    # loan.payment_history = history
    db.session.add(payment_entry)
    db.session.commit()
    
    return jsonify({'message': 'Payment updated successfully'}), 200
  
@app.route('/api/send-reminders', methods=['GET'])
@jwt_required()
def trigger_reminders():
    try:
        from reminders import send_due_reminders
        reminders_sent = send_due_reminders()  # <-- Get status
        if reminders_sent == 0:
            return jsonify({'message': 'No reminders due today'}), 200
        return jsonify({'message': f'Reminders sent to {reminders_sent} user(s)'}), 200
    except Exception as e:
        print(f"Error sending reminders: {e}")
        return jsonify({'message': 'Failed to send reminders'}), 500
   
if __name__ == '__main__':
    app.run(debug=True)
 