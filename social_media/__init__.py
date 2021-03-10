
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

from flask_admin.contrib.sqla import ModelView
from flask_moment import Moment
from social_media.config import Config







db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category =  'notice'
migrate = Migrate()
moment = Moment()

mail = Mail()




def create_app(config_class = Config):
    
    app = Flask(__name__)

    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
   
    from social_media.users.routes import users


    from social_media.post.routes import posts

    from social_media.comment.routes import comments
    from social_media.main.routes import main
    from social_media.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(comments)
    app.register_blueprint(errors)

    return app

