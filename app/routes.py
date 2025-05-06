from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt
from app.forms import LoginForm, SignupForm, RequestResetForm, ResetPasswordForm
from app.models import User, Transaction
from datetime import datetime, timedelta
import requests
from app.utils import send_reset_email
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt
import io
import base64
import os
from threading import Thread

bp = Blueprint('main', __name__)

# Background email thread
def start_email_thread(app):
    with app.app_context():
        if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            thread = Thread(target=send_monthly_report)
            thread.daemon = True
            thread.start()

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('signup.html', form=form)

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('If an account exists with that email, a reset link has been sent.', 'info')
        return redirect(url_for('main.login'))
    return render_template('forgot_password.html', form=form)

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('main.forgot_password'))
        
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_token.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.budget_set:
        flash('Please set your monthly budget to continue', 'warning')
    return render_template('dashboard.html')

@bp.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    try:
        monthly_budget = float(request.form.get('monthly_budget'))
        report_email = request.form.get('report_email')
        
        current_user.monthly_budget = monthly_budget
        current_user.report_email = report_email
        current_user.budget_set = True
        db.session.commit()
        
        flash('Budget settings saved successfully!', 'success')
    except ValueError:
        flash('Invalid budget amount', 'danger')
    return redirect(url_for('main.dashboard'))

@bp.route('/api/data')
@login_required
def get_dashboard_data():
    try:
        api_data = requests.get('https://pgbankapi.onrender.com/transactions', timeout=5).json()
        
        transactions = []
        for t in api_data.get('transactions', []):
            transactions.append({
                'merchant': t['merchant'],
                'amount': t['amount'],
                'type': t['type'],
                'time': t['time']
            })
            db.session.add(Transaction(
                user_id=current_user.id,
                merchant=t['merchant'],
                amount=t['amount'],
                type=t['type'],
                time=datetime.strptime(t['time'], '%Y-%m-%d %H:%M:%S')
            ))
        
        db.session.commit()
        
        start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        monthly_spent = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.time >= start_date,
            Transaction.type == 'debit'
        ).scalar() or 0
        
        return jsonify({
            'balance': api_data.get('balance', 0),
            'transactions': transactions[-10:],
            'monthly_spent': monthly_spent
        })
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Unable to fetch transaction data'}), 500

@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def send_monthly_report():
    while True:
        try:
            now = datetime.now()
            next_month = now.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
            
            if now.day == last_day.day and now.hour == 20:
                users = User.query.filter_by(budget_set=True).all()
                for user in users:
                    send_user_report(user)
                time.sleep(86400)  
            time.sleep(3600) 
        except Exception as e:
            print(f"Error in monthly report: {e}")
            time.sleep(3600)

def send_user_report(user):
    try:
        start_date = datetime.now().replace(day=1)
        transactions = Transaction.query.filter(
            Transaction.user_id == user.id,
            Transaction.time >= start_date
        ).all()
        
        merchants = {}
        daily_spending = {}
        
        for t in transactions:
            if t.type == 'debit':
                merchants[t.merchant] = merchants.get(t.merchant, 0) + t.amount
                day = t.time.strftime('%Y-%m-%d')
                daily_spending[day] = daily_spending.get(day, 0) + t.amount
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        top_merchants = sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:5]
        ax1.bar([m[0] for m in top_merchants], [m[1] for m in top_merchants])
        ax1.set_title('Top 5 Merchants')
        ax1.set_ylabel('Amount Spent (₹)')
        
        dates = sorted(daily_spending.keys())
        ax2.plot(dates, [daily_spending[d] for d in dates])
        ax2.set_title('Daily Spending Trend')
        ax2.set_ylabel('Amount Spent (₹)')
        plt.xticks(rotation=45)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        chart_image = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_FROM', 'reports@expenserfx.com')
        msg['To'] = user.report_email
        msg['Subject'] = f'ExpenserFX Monthly Report - {now.strftime("%B %Y")}'
        
        html = f"""<html><body>
            <h2>Monthly Spending Report</h2>
            <p>Hello {user.username}, here's your spending summary:</p>
            <h3>Top Merchants</h3>
            <ol>{"".join(f"<li>{m[0]}: ₹{m[1]}</li>" for m in top_merchants)}</ol>
            <h3>Spending Trend</h3>
            <img src="data:image/png;base64,{chart_image}">
            <p>Total spent: ₹{sum(merchants.values())}</p>
            <p>Remaining budget: ₹{user.monthly_budget - sum(merchants.values())}</p>
            <footer><p>Thank you for using ExpenserFX!</p></footer>
        </body></html>"""
        
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP(os.getenv('SMTP_SERVER', 'smtp.gmail.com'), 
                         int(os.getenv('SMTP_PORT', 587))) as server:
            server.starttls()
            server.login(os.getenv('SMTP_USERNAME'), 
                        os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending report to {user.email}: {e}")