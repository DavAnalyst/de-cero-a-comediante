"""
Seed script for production: creates admin user and the main course if they don't exist.
Run once via Railway pre-deploy or terminal: python seed_prod.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db, bcrypt
from app.models import User, Course

app = create_app(os.environ.get("FLASK_ENV", "production"))

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "yeisonniev@gmail.com")
ADMIN_NAME = os.environ.get("ADMIN_NAME", "David Nieves")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

with app.app_context():
    # Admin user
    if not User.query.filter_by(email=ADMIN_EMAIL).first():
        if not ADMIN_PASSWORD:
            print("ERROR: set ADMIN_PASSWORD env var to create admin user")
            sys.exit(1)
        hashed = bcrypt.generate_password_hash(ADMIN_PASSWORD).decode("utf-8")
        admin = User(email=ADMIN_EMAIL, name=ADMIN_NAME, password_hash=hashed, is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin created: {ADMIN_EMAIL}")
    else:
        print(f"Admin already exists: {ADMIN_EMAIL}")

    # Main course
    if not Course.query.first():
        course = Course(
            title="De Cero a Comediante",
            description="El curso completo de stand-up comedy. Aprende a construir tus bits, conectar con el publico y subirte al escenario con confianza.",
            price_cop=199000,
            is_published=True,
        )
        db.session.add(course)
        db.session.commit()
        print(f"Course created: {course.title} (id={course.id})")
    else:
        print("Course already exists")