# create_admin.py
from app import app, db, bcrypt
from app.models import User

with app.app_context():
    # Create admin user
    hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
    admin = User(username='admin', email='admin@jobportal.com', usertype='Admin', password=hashed_password, is_admin=True)

    db.session.add(admin)
    db.session.commit()
    print("✅ Admin user created!")
