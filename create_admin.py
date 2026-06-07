from app import app, db, bcrypt
from app import User

with app.app_context():
    # Check if admin already exists
    existing = User.query.filter_by(email='admin@learnnaija.com').first()
    if existing:
        print('Admin already exists!')
    else:
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
        print('Admin created successfully!')