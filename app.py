from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import os

# Initialize the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'nigeria-learning-system-2024'

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///learning.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ========== DATABASE MODELS ==========

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    university = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(10), default='student')
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(10), nullable=False)
    resource_link = db.Column(db.String(300), nullable=False)
    course_type = db.Column(db.String(50), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class LearningProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    learning_style = db.Column(db.String(50), nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    date_recommended = db.Column(db.DateTime, default=datetime.utcnow)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    status = db.Column(db.String(20), default='not started')
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ========== ROUTES ==========

@app.route('/setup')
def setup():
    try:
        db.create_all()
        admin_exists = User.query.filter_by(email='admin@learnnaija.com').first()
        if not admin_exists:
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(
                full_name='Admin User',
                email='admin@learnnaija.com',
                password=hashed_password,
                university='LearnNaija HQ',
                department='Administration',
                level='N/A',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            return 'Database setup complete and admin created successfully!'
        return 'Database already setup!'
    except Exception as e:
        return f'Error: {str(e)}'

@app.route('/')
def home():
    return render_template('home.html')

# ========== REGISTER ==========
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        university = request.form.get('university')
        department = request.form.get('department')
        level = request.form.get('level')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered! Please login.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            full_name=full_name,
            email=email,
            password=hashed_password,
            university=university,
            department=department,
            level=level,
            role='student'
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ========== LOGIN ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful! Welcome back.', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# ========== LOGOUT ==========
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# ========== STUDENT DASHBOARD ==========
@app.route('/dashboard')
@login_required
def student_dashboard():
    return render_template('dashboard.html')

# ========== QUIZ ==========
@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'POST':
        answers = []
        for i in range(1, 11):
            answer = request.form.get(f'q{i}')
            answers.append(answer)

        visual = answers.count('visual')
        reading = answers.count('reading')
        practical = answers.count('practical')

        if visual >= reading and visual >= practical:
            learning_style = 'Visual'
        elif reading >= visual and reading >= practical:
            learning_style = 'Reading'
        else:
            learning_style = 'Practical'

        existing_profile = LearningProfile.query.filter_by(user_id=current_user.id).first()
        if existing_profile:
            existing_profile.learning_style = learning_style
        else:
            profile = LearningProfile(
                user_id=current_user.id,
                learning_style=learning_style
            )
            db.session.add(profile)
        db.session.commit()

        flash(f'Quiz completed! Your learning style is: {learning_style}', 'success')
        return redirect(url_for('recommendations'))

    return render_template('quiz.html')

# ========== RECOMMENDATIONS ==========
@app.route('/recommendations')
@login_required
def recommendations():
    profile = LearningProfile.query.filter_by(user_id=current_user.id).first()
    recommendations = []
    if profile:
        recommendations = Course.query.filter_by(
            course_type=profile.learning_style
        ).all()
    return render_template('recommendations.html',
                           profile=profile,
                           recommendations=recommendations)

# ========== ADMIN ROUTES ==========
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied! Admins only.', 'danger')
        return redirect(url_for('student_dashboard'))
    students = User.query.filter_by(role='student').all()
    total_students = len(students)
    total_courses = Course.query.count()
    total_profiles = LearningProfile.query.count()
    total_recommendations = Recommendation.query.count()
    return render_template('admin.html',
                           students=students,
                           total_students=total_students,
                           total_courses=total_courses,
                           total_profiles=total_profiles,
                           total_recommendations=total_recommendations)

@app.route('/admin/add-course', methods=['POST'])
@login_required
def add_course():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('student_dashboard'))
    title = request.form.get('title')
    description = request.form.get('description')
    subject = request.form.get('subject')
    level = request.form.get('level')
    course_type = request.form.get('course_type')
    resource_link = request.form.get('resource_link')
    new_course = Course(
        title=title,
        description=description,
        subject=subject,
        level=level,
        course_type=course_type,
        resource_link=resource_link
    )
    db.session.add(new_course)
    db.session.commit()
    flash('Course added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# TEMPLATE FILTER
@app.template_filter('get_profile')
def get_profile(user_id):
    return LearningProfile.query.filter_by(user_id=user_id).first()

# ========== RUN APP ==========
if __name__ == '__main__':
    app.run(debug=True)