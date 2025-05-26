from datetime import datetime, timedelta
from app import app  # Import the Flask app instance
from models import db, Loan, User
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# ---- Email Configuration ----
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# ---- Twilio Configuration ----
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')


def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        print(f"📧 Email sent to {to_email}")


def send_sms(to_phone, body):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=body,
        from_=TWILIO_PHONE_NUMBER,
        to=to_phone
    )
    print(f"📱 SMS sent to {to_phone}: SID {message.sid}")


def send_due_reminders():
    with app.app_context():
        today = datetime.now().date()
        next_week = today + timedelta(days=7)

        loans = Loan.query.all()
        due_loans = []

        for loan in loans:
            # Calculate the next expected due date
            if loan.last_payment_date:
                next_due_date = loan.last_payment_date.date() + timedelta(days=7)
            else:
                next_due_date = loan.registered_date.date() + timedelta(days=7)

            # Check if next_due_date falls within today and the next 7 days
            if today <= next_due_date <= next_week and loan.amount_left > 0:
                due_loans.append(loan)

        count = 0

        for loan in due_loans:
            borrower_name = loan.name
            due_date = next_due_date.strftime("%d/%m/%Y")
            phone = loan.phone
            email = loan.email

            # ✅ Weekly payment calculation
            total_to_pay = loan.original_amount + (loan.original_amount * loan.interest / 100)
            weekly_due = round(total_to_pay / loan.duration, 2)

            subject = f"⏰ Weekly Payment Reminder - {borrower_name}"
            message = (
                f"Hello {borrower_name},\n\n"
                f"This is a reminder that a payment of ₦{weekly_due:,.2f} "
                f"is due by {due_date} as part of your loan repayment.\n"
                f"Please make the payment to stay on track.\n\n"
                f"Loan Details:\n"
                f"- Total Loan: ₦{loan.original_amount:,.2f}\n"
                f"- Interest: {loan.interest}%\n"
                f"- Duration: {loan.duration} week(s)\n"
                f"- Amount Left: ₦{loan.amount_left:,.2f}\n\n"
                f"Thank you."
            )

            if email:
                try:
                    send_email(email, subject, message)
                    count += 1
                except Exception as e:
                    print(f"❌ Failed to send email to {email}: {e}")

            if phone:
                try:
                    send_sms(phone, message)
                    count += 1
                except Exception as e:
                    print(f"❌ Failed to send SMS to {phone}: {e}")

        return count
