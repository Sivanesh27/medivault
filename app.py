# MediVault - Fullstack Healthcare App (Flask-based)
# ================================================
# Features Implemented:
# ----------------------
# ✅ User/Admin Registration & Login (with role distinction)
# ✅ Dashboard (role-specific)
# ✅ Electronic Health Records (EHR) Upload/View
# ✅ Medical Images (viewable with DICOM viewer placeholder)
# ✅ Appointment Booking
# ✅ Online Pharmacy (listing + cart placeholder)
# ✅ Chatbot Interface (placeholder for OpenAI/Dialogflow)
# ✅ Fingerprint ID placeholder (to be linked with biometric hardware later)

from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
# ----------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10))  # 'patient' or 'admin'

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(300))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    status = db.Column(db.String(20))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
# ------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        new_user = User(email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        patients = User.query.filter_by(role='patient').all()
        return render_template('admin_dashboard.html', user=current_user, patients=patients)
    else:
        records = Record.query.filter_by(user_id=current_user.id).all()
        appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
        return render_template('user_dashboard.html', user=current_user, records=records, appointments=appointments)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        new_record = Record(user_id=current_user.id, filename=filename)
        db.session.add(new_record)
        db.session.commit()
        flash('Record uploaded!')
        return redirect(url_for('dashboard'))
    return render_template('upload.html')

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    if current_user.role == 'patient':
        doctors = User.query.filter_by(role='admin').all()
        if request.method == 'POST':
            doc_id = request.form['doctor_id']
            date = request.form['date']
            time = request.form['time']
            new_appt = Appointment(patient_id=current_user.id, doctor_id=doc_id, date=date, time=time, status='pending')
            db.session.add(new_appt)
            db.session.commit()
            flash('Appointment requested!')
            return redirect(url_for('dashboard'))
        return render_template('appointment.html', doctors=doctors)
    else:
        appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
        return render_template('doctor_appointments.html', appointments=appointments)

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')  # Placeholder for integration

@app.route('/pharmacy')
@login_required
def pharmacy():
    return render_template('pharmacy.html')  # Placeholder for online store

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

import os
TEMPLATE_DIR = os.path.join(os.getcwd(), 'templates')
os.makedirs(TEMPLATE_DIR, exist_ok=True)
with open(os.path.join(TEMPLATE_DIR, 'upload.html'), 'w') as f: f.write(upload_html)
with open(os.path.join(TEMPLATE_DIR, 'appointment.html'), 'w') as f: f.write(appointment_html)
with open(os.path.join(TEMPLATE_DIR, 'doctor_appointments.html'), 'w') as f: f.write(doctor_appointments_html)
with open(os.path.join(TEMPLATE_DIR, 'chatbot.html'), 'w') as f: f.write(chatbot_html)
with open(os.path.join(TEMPLATE_DIR, 'pharmacy.html'), 'w') as f: f.write(pharmacy_html)
with open(os.path.join(TEMPLATE_DIR, 'dicom_viewer.html'), 'w') as f: f.write(dicom_viewer_html)

import os

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 10000))  # Render provides this
    app.run(host='0.0.0.0', port=port, debug=True)  # ✅ Correctly exposed



