import os
import json
import secrets
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Configuration
SHEETY_API_URL = os.getenv('SHEETY_API_URL')
SHEETY_TOKEN = os.getenv('SHEETY_TOKEN')
MAILJET_API_KEY = os.getenv('MAILJET_API_KEY')
MAILJET_SECRET_KEY = os.getenv('MAILJET_SECRET_KEY')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

# In-memory storage for demo (in production, this would be a database)
users = {}
records = {}
verification_codes = {}

@app.route('/')
def homepage():
    """Homepage showing count of approved public records"""
    approved_count = len([r for r in records.values() if r.get('status') == 'approved'])
    return render_template('homepage.html', approved_count=approved_count)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """First step: User signup to get verification code"""
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        institution = request.form.get('institution')
        
        if not email or not name:
            flash('Email and name are required')
            return render_template('signup.html')
        
        # Generate verification code
        code = secrets.token_urlsafe(8)
        verification_codes[email] = {
            'code': code,
            'name': name,
            'institution': institution,
            'created': datetime.now(),
            'verified': False
        }
        
        # Send verification email (using Mailjet)
        send_verification_email(email, name, code)
        
        flash('Verification code sent to your email!')
        return redirect(url_for('verify'))
    
    return render_template('signup.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """Second step: Verify code and enable submissions"""
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')
        
        if email in verification_codes and verification_codes[email]['code'] == code:
            # Mark as verified and create user
            user_data = verification_codes[email]
            user_data['verified'] = True
            users[email] = user_data
            session['user'] = email
            
            flash('Account verified! You can now submit records.')
            return redirect(url_for('submit'))
        else:
            flash('Invalid email or verification code')
    
    return render_template('verify.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    """Submit new records (requires verified user)"""
    if 'user' not in session:
        flash('Please sign up and verify your account first')
        return redirect(url_for('signup'))
    
    if request.method == 'POST':
        record_data = {
            'id': secrets.token_urlsafe(8),
            'submitter': session['user'],
            'algorithm': request.form.get('algorithm'),
            'sequence': request.form.get('sequence'),
            'allele': request.form.get('allele'),
            'result_type': request.form.get('result_type'),  # 'false_positive' or 'false_negative'
            'expected_result': request.form.get('expected_result'),
            'actual_result': request.form.get('actual_result'),
            'description': request.form.get('description'),
            'status': 'pending',
            'submitted': datetime.now().isoformat()
        }
        
        records[record_data['id']] = record_data
        
        # Send to Google Sheets via Sheety API
        save_to_sheets(record_data)
        
        # Notify via Slack for approval
        notify_slack_approval(record_data)
        
        flash('Record submitted successfully! It will be reviewed before publication.')
        return redirect(url_for('homepage'))
    
    return render_template('submit.html')

@app.route('/browse')
def browse():
    """Browse and search approved records"""
    search_query = request.args.get('q', '').lower()
    algorithm_filter = request.args.get('algorithm', '')
    result_type_filter = request.args.get('result_type', '')
    
    # Filter approved records
    approved_records = [r for r in records.values() if r.get('status') == 'approved']
    
    if search_query:
        approved_records = [r for r in approved_records 
                          if search_query in r.get('sequence', '').lower() 
                          or search_query in r.get('description', '').lower()]
    
    if algorithm_filter:
        approved_records = [r for r in approved_records 
                          if r.get('algorithm') == algorithm_filter]
    
    if result_type_filter:
        approved_records = [r for r in approved_records 
                          if r.get('result_type') == result_type_filter]
    
    # Get unique values for filters
    algorithms = list(set(r.get('algorithm') for r in records.values() if r.get('status') == 'approved'))
    result_types = ['false_positive', 'false_negative']
    
    return render_template('browse.html', 
                         records=approved_records,
                         algorithms=algorithms,
                         result_types=result_types,
                         current_search=search_query,
                         current_algorithm=algorithm_filter,
                         current_result_type=result_type_filter)

@app.route('/record/<record_id>')
def record_view(record_id):
    """View individual record details"""
    record = records.get(record_id)
    if not record or record.get('status') != 'approved':
        flash('Record not found or not approved')
        return redirect(url_for('browse'))
    
    return render_template('record_view.html', record=record)

@app.route('/approve/<record_id>')
def approve_record(record_id):
    """Approve a record (would be called via Slack webhook)"""
    if record_id in records:
        records[record_id]['status'] = 'approved'
        records[record_id]['approved'] = datetime.now().isoformat()
        flash('Record approved!')
    return redirect(url_for('homepage'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    flash('Logged out successfully')
    return redirect(url_for('homepage'))

def send_verification_email(email, name, code):
    """Send verification email using Mailjet API"""
    if not MAILJET_API_KEY or not MAILJET_SECRET_KEY:
        print(f"Demo mode: Verification code for {email}: {code}")
        return
    
    try:
        data = {
            'Messages': [{
                'From': {'Email': 'noreply@example.com', 'Name': 'False Positives/Negatives'},
                'To': [{'Email': email, 'Name': name}],
                'Subject': 'Verify your account',
                'TextPart': f'Hello {name},\n\nYour verification code is: {code}\n\nPlease use this code to verify your account.',
                'HTMLPart': f'<h3>Hello {name},</h3><p>Your verification code is: <strong>{code}</strong></p><p>Please use this code to verify your account.</p>'
            }]
        }
        
        response = requests.post(
            'https://api.mailjet.com/v3.1/send',
            auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY),
            json=data
        )
        print(f"Email sent: {response.status_code}")
    except Exception as e:
        print(f"Email error: {e}")

def save_to_sheets(record_data):
    """Save record to Google Sheets using Sheety API"""
    if not SHEETY_API_URL or not SHEETY_TOKEN:
        print(f"Demo mode: Would save to sheets: {record_data['id']}")
        return
    
    try:
        headers = {'Authorization': f'Bearer {SHEETY_TOKEN}'}
        response = requests.post(SHEETY_API_URL, headers=headers, json={'record': record_data})
        print(f"Sheets save: {response.status_code}")
    except Exception as e:
        print(f"Sheets error: {e}")

def notify_slack_approval(record_data):
    """Send Slack notification for record approval"""
    if not SLACK_WEBHOOK_URL:
        print(f"Demo mode: Would notify Slack for approval: {record_data['id']}")
        return
    
    try:
        message = {
            'text': f"New record submitted for approval",
            'attachments': [{
                'color': 'warning',
                'fields': [
                    {'title': 'Algorithm', 'value': record_data.get('algorithm'), 'short': True},
                    {'title': 'Type', 'value': record_data.get('result_type'), 'short': True},
                    {'title': 'Sequence', 'value': record_data.get('sequence')[:50] + '...', 'short': False},
                    {'title': 'Submitter', 'value': record_data.get('submitter'), 'short': True}
                ],
                'actions': [{
                    'type': 'button',
                    'text': 'Approve',
                    'url': f"{request.url_root}approve/{record_data['id']}"
                }]
            }]
        }
        
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        print(f"Slack notification: {response.status_code}")
    except Exception as e:
        print(f"Slack error: {e}")

if __name__ == '__main__':
    app.run(debug=True)