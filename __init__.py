from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from os import path
from flask_login import LoginManager
from sqlalchemy.exc import OperationalError

#SQLAlchemy is an open-source SQL toolkit and object-relational mapper for the Python programming language released under the MIT License.
db = SQLAlchemy()
DB_NAME = "database.db"

#Application Factory https://flask.palletsprojects.com/en/2.3.x/patterns/appfactories/
def create_app():
    app = Flask(__name__)
    app.config['SECURITY_PASSWORD_HASH'] = 'argon2'
    app.config['SECURITY_PASSWORD_ARGON2_BACKEND'] = 'argon2_cffi'
    app.config['SECRET_KEY'] = 'aswiods fkdlnansf'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    
    from .views import views
    from .auth import auth
    from .health import health
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(health, url_prefix='/')

    from .models import User 
    from .models import Note
    from .models import Contact
    from .models import Recipe
    from .models import Instruction
    from .models import CookingTime
    from .models import Ingredient
    from .models import Unit
    
    with app.app_context():
        try:
            db.drop_all()
        except OperationalError as e:
            # Handle the exception, e.g., log the error
            app.logger.error(f"Error dropping tables: {e}")
        db.create_all()
        # Check if the User table exists
        inspector = inspect(db.engine)
        if not inspector.has_table(User.__tablename__):
            # Table does not exist, perform necessary actions
            pass

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
 
def create_database(app):
    if not path.exists(DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')
        
        
