from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from google import genai




db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'gdjfngjkdfsg;sdfg'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/database.db'
    
    from .auth import auth 
    from .routes import routes
    from .models import models
    from .forms import forms

    app.register_blueprint(auth)
    app.register_blueprint(routes)
    app.register_blueprint(models)
    app.register_blueprint(forms)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    from .models import User
    

    

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    

    return app
