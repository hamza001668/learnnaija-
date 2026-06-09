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
    @app.route('/add-courses')
def add_courses_route():
    try:
        existing_titles = [c.title for c in Course.query.all()]
        courses = [
            Course(title='Data Structures Visualized', description='Learn data structures through beautiful animations and visual diagrams that make complex topics easy to understand.', subject='Computer Science', level='200 Level', resource_link='https://visualgo.net', course_type='Visual'),
            Course(title='Mathematics for Engineers (Video Lectures)', description='Video based mathematics course covering calculus, algebra and statistics with visual explanations for engineering students.', subject='Mathematics', level='100 Level', resource_link='https://www.khanacademy.org/math', course_type='Visual'),
            Course(title='Circuit Analysis Video Tutorials', description='Step by step video tutorials on electrical circuit analysis with visual diagrams and animations for engineering students.', subject='Electrical Engineering', level='200 Level', resource_link='https://www.youtube.com/watch?v=mc979OhitAg', course_type='Visual'),
            Course(title='Human Anatomy Video Series', description='Detailed video lectures on human anatomy with 3D visualizations and diagrams for medical and nursing students.', subject='Medicine', level='200 Level', resource_link='https://www.khanacademy.org/science/health-and-medicine', course_type='Visual'),
            Course(title='Business Management Video Course', description='Comprehensive video lectures on business management principles and leadership for Nigerian students.', subject='Business Administration', level='200 Level', resource_link='https://www.coursera.org/learn/wharton-business-foundations', course_type='Visual'),
            Course(title='Geography of Nigeria Video Lectures', description='Comprehensive video lectures covering physical and human geography of Nigeria including landforms, climate and natural resources.', subject='Geography', level='100 Level', resource_link='https://www.youtube.com/watch?v=7RMxGCU1GhQ', course_type='Visual'),
            Course(title='Physics Video Lectures for Beginners', description='Engaging video lectures covering fundamental physics concepts including mechanics, waves and electricity with visual demonstrations.', subject='Physics', level='100 Level', resource_link='https://www.khanacademy.org/science/physics', course_type='Visual'),
            Course(title='Chemistry Video Tutorials', description='Comprehensive video tutorials covering organic and inorganic chemistry with visual molecular diagrams and laboratory demonstrations.', subject='Chemistry', level='100 Level', resource_link='https://www.khanacademy.org/science/chemistry', course_type='Visual'),
            Course(title='Architecture Design Video Course', description='Visual video course covering architectural design principles, building structures and urban planning for architecture students.', subject='Architecture', level='200 Level', resource_link='https://www.youtube.com/watch?v=Jrq7RQWVZMQ', course_type='Visual'),
            Course(title='Mechanical Engineering Video Lectures', description='Comprehensive video lectures covering mechanical engineering principles including thermodynamics and fluid mechanics.', subject='Mechanical Engineering', level='200 Level', resource_link='https://www.youtube.com/watch?v=SFW4oiHMSq0', course_type='Visual'),
            Course(title='Economics Video Lectures', description='Engaging video lectures covering micro and macroeconomics principles and Nigerian economic policies with visual charts.', subject='Economics', level='200 Level', resource_link='https://www.khanacademy.org/economics-finance-domain', course_type='Visual'),
            Course(title='Statistics and Data Visualization Course', description='Comprehensive video course covering statistics, data analysis and visualization techniques for university students.', subject='Mathematics', level='300 Level', resource_link='https://www.khanacademy.org/math/statistics-probability', course_type='Visual'),
            Course(title='Accounting and Finance Video Course', description='Comprehensive video lectures covering accounting principles and financial management for accounting students.', subject='Accounting', level='100 Level', resource_link='https://www.youtube.com/watch?v=yYX4bvQSqbo', course_type='Visual'),
            Course(title='Nursing Care Video Tutorials', description='Detailed video tutorials covering nursing care procedures and clinical skills for Nigerian nursing students.', subject='Nursing', level='200 Level', resource_link='https://www.youtube.com/watch?v=eBzMByybBg0', course_type='Visual'),
            Course(title='Introduction to Computer Science (MIT Notes)', description='Comprehensive written lecture notes from MIT covering all fundamental Computer Science concepts for university students.', subject='Computer Science', level='100 Level', resource_link='https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/', course_type='Reading'),
            Course(title='Business Law and Ethics Textbook', description='A complete reading resource covering Nigerian business law, corporate governance and professional ethics for business students.', subject='Business Administration', level='300 Level', resource_link='https://openstax.org/books/business-law-i-essentials/pages/1-introduction', course_type='Reading'),
            Course(title='Engineering Mathematics Textbook', description='Free online textbook covering all engineering mathematics topics with detailed written explanations for Nigerian students.', subject='Mathematics', level='200 Level', resource_link='https://openstax.org/subjects/math', course_type='Reading'),
            Course(title='Principles of Economics (Written Course)', description='Detailed written course covering micro and macroeconomics principles relevant to the Nigerian economy.', subject='Economics', level='100 Level', resource_link='https://openstax.org/books/principles-economics-3e/pages/1-introduction', course_type='Reading'),
            Course(title='Introduction to Law (Reading Materials)', description='Comprehensive reading materials covering Nigerian law, legal systems and constitutional law for law students.', subject='Law', level='100 Level', resource_link='https://www.lawteacher.net/free-law-essays/introduction-to-law/', course_type='Reading'),
            Course(title='Introduction to Microbiology Study Notes', description='Detailed written study notes covering microbiology concepts, bacteria, viruses and laboratory techniques for science students.', subject='Microbiology', level='300 Level', resource_link='https://www.ncbi.nlm.nih.gov/books/NBK7627/', course_type='Reading'),
            Course(title='Geography of Africa Study Notes', description='Detailed written study notes covering the geography of Africa including physical features, climate zones and economic resources.', subject='Geography', level='200 Level', resource_link='https://www.nationalgeographic.org/encyclopedia/africa/', course_type='Reading'),
            Course(title='Introduction to Mass Communication (Study Guide)', description='Comprehensive reading materials covering mass communication theories, media ethics and journalism in the Nigerian context.', subject='Mass Communication', level='200 Level', resource_link='https://www.open.edu/openlearn/society-politics-law/media-studies/content-section-0', course_type='Reading'),
            Course(title='Introduction to Agriculture (Study Materials)', description='Comprehensive reading materials covering crop production, soil science and agricultural economics relevant to Nigerian farming.', subject='Agriculture', level='100 Level', resource_link='https://www.fao.org/home/en/', course_type='Reading'),
            Course(title='Introduction to Pharmacy (Study Notes)', description='Detailed written study notes covering pharmacology, drug interactions and pharmaceutical chemistry for Nigerian pharmacy students.', subject='Pharmacy', level='300 Level', resource_link='https://www.pharmpress.com/free-resources', course_type='Reading'),
            Course(title='Introduction to Education (Study Guide)', description='Comprehensive reading materials covering educational psychology, teaching methods and curriculum development for Nigerian students.', subject='Education', level='100 Level', resource_link='https://www.open.edu/openlearn/education-development/education/content-section-0', course_type='Reading'),
            Course(title='Introduction to Physics (Study Notes)', description='Detailed written study notes covering fundamental physics concepts including mechanics, thermodynamics and electricity.', subject='Physics', level='100 Level', resource_link='https://openstax.org/books/university-physics-volume-1/pages/1-introduction', course_type='Reading'),
            Course(title='Mechanical Engineering Textbook', description='Comprehensive written textbook covering mechanical engineering fundamentals including thermodynamics and fluid mechanics.', subject='Mechanical Engineering', level='300 Level', resource_link='https://openstax.org/subjects/science', course_type='Reading'),
            Course(title='Python Programming Projects for Beginners', description='Hands on Python programming course where you build real projects from day one perfect for practical learners.', subject='Computer Science', level='200 Level', resource_link='https://www.freecodecamp.org/learn/scientific-computing-with-python/', course_type='Practical'),
            Course(title='Web Development Bootcamp (Hands-on)', description='Build real websites from scratch using HTML, CSS and JavaScript through practical hands on exercises.', subject='Computer Science', level='300 Level', resource_link='https://www.freecodecamp.org/learn/responsive-web-design/', course_type='Practical'),
            Course(title='Accounting Practice Exercises', description='Practical accounting exercises covering bookkeeping, financial statements and Nigerian tax calculations.', subject='Accounting', level='200 Level', resource_link='https://www.accountingcoach.com/accounting-basics/quiz', course_type='Practical'),
            Course(title='Civil Engineering Lab Projects', description='Practical civil engineering projects and experiments covering structural analysis and material testing.', subject='Civil Engineering', level='300 Level', resource_link='https://www.engineeringintro.com', course_type='Practical'),
            Course(title='Business Plan Development Workshop', description='Practical workshop where you develop a real business plan step by step relevant to the Nigerian market.', subject='Business Administration', level='300 Level', resource_link='https://www.sba.gov/business-guide/plan-your-business/write-your-business-plan', course_type='Practical'),
            Course(title='GIS and Mapping Practical Course', description='Hands on practical course on Geographic Information Systems and digital mapping techniques for geography students.', subject='Geography', level='300 Level', resource_link='https://www.esri.com/training/catalog/search/', course_type='Practical'),
            Course(title='Medical Clinical Practice Guide', description='Practical clinical skills guide for medical students covering patient examination and diagnosis in Nigerian hospitals.', subject='Medicine', level='400 Level', resource_link='https://www.amboss.com', course_type='Practical'),
            Course(title='Electrical Engineering Circuit Lab', description='Hands on electrical engineering laboratory exercises covering circuit design and troubleshooting for Nigerian students.', subject='Electrical Engineering', level='300 Level', resource_link='https://www.tinkercad.com/circuits', course_type='Practical'),
            Course(title='Economics Data Analysis Workshop', description='Practical workshop covering economic data analysis, research methods and statistical tools for Nigerian economic studies.', subject='Economics', level='300 Level', resource_link='https://www.worldbank.org/en/research', course_type='Practical'),
            Course(title='Chemistry Laboratory Experiments', description='Hands on chemistry laboratory experiments covering titration and chemical reactions for Nigerian science students.', subject='Chemistry', level='200 Level', resource_link='https://www.labxchange.org', course_type='Practical'),
            Course(title='Agriculture Field Practice Guide', description='Hands on practical guide covering crop planting, soil testing and farm management for Nigerian agriculture students.', subject='Agriculture', level='200 Level', resource_link='https://www.agrifarming.in', course_type='Practical'),
            Course(title='Law Moot Court Practice', description='Practical guide for law students covering courtroom procedures and case studies relevant to Nigerian law.', subject='Law', level='300 Level', resource_link='https://www.lawteacher.net/free-law-essays/', course_type='Practical'),
            Course(title='Teaching Practice Workshop', description='Hands on teaching practice workshop covering lesson planning and classroom management for Nigerian education students.', subject='Education', level='300 Level', resource_link='https://www.teachervision.com', course_type='Practical'),
            Course(title='Microbiology Laboratory Practical Guide', description='Hands on laboratory practical guide covering microscopy and microbial analysis for Nigerian science students.', subject='Microbiology', level='300 Level', resource_link='https://www.microbiologyonline.org', course_type='Practical'),
            Course(title='Mass Communication Media Production', description='Hands on media production workshop covering radio broadcasting and digital journalism for Nigerian students.', subject='Mass Communication', level='300 Level', resource_link='https://www.coursera.org/learn/journalism', course_type='Practical'),
            Course(title='Architecture Design Studio Project', description='Hands on architecture design studio project covering building design and construction techniques for Nigerian students.', subject='Architecture', level='300 Level', resource_link='https://www.archdaily.com', course_type='Practical'),
        ]
        added = 0
        for course in courses:
            if course.title not in existing_titles:
                db.session.add(course)
                added += 1
        db.session.commit()
        return f'Done! Added {added} new courses! Total now: {Course.query.count()}'
    except Exception as e:
        return f'Error: {str(e)}'
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