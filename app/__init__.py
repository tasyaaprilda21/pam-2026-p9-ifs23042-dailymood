from flask import Flask
from flask_cors import CORS
from app.extensions import Base, engine
from app.routes.journal_routes import journal_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    Base.metadata.create_all(bind=engine)
    _seed_admin()
    app.register_blueprint(journal_bp)
    return app

def _seed_admin():
    from app.extensions import SessionLocal
    from app.models.user import User
    session = SessionLocal()
    try:
        if not session.query(User).filter_by(username="admin").first():
            admin = User(username="admin", password="admin123")
            session.add(admin)
            session.commit()
            print("Admin user created!")
    finally:
        session.close()