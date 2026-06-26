from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from config import Config
import firebase_admin
from firebase_admin import credentials, firestore
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()
socketio = SocketIO(cors_allowed_origins="*")

from flask_mail import Mail
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    login_manager.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)

    # Initialize Firebase
    firebase_key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'serviceAccountKey.json')
    if os.path.exists(firebase_key_path) and not firebase_admin._apps:
        cred = credentials.Certificate(firebase_key_path)
        firebase_admin.initialize_app(cred)
        app.db_firestore = firestore.client()
        print("Firebase initialized successfully.")
    else:
        app.db_firestore = None
        print("Warning: serviceAccountKey.json not found or Firebase already initialized. Firestore disabled.")

    from app.main.routes import main
    from app.auth.routes import auth
    from app.api.routes import api
    from app import models  # Register user_loader

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api, url_prefix='/api')

    return app
