# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect          
from flask_wtf.csrf import generate_csrf   

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"

csrf = CSRFProtect()                       


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)                     

    # make {{ csrf_token() }} available in any Jinja template
    @app.context_processor                 
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    # blueprints
    from . import routes
    app.register_blueprint(routes.bp)

    # create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
