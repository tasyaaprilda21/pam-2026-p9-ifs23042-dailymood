from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app)

    from .routes.auth import auth_bp
    from .routes.journals import journals_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(journals_bp, url_prefix='/journals')

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app

def _seed_admin():
    from .models import User
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created!')