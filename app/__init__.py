# -*- coding: UTF-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
bootstrap = Bootstrap()
moment = Moment()
login_manager = LoginManager()
db = SQLAlchemy()

photos = UploadSet('photos', IMAGES)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    db.init_app(app)
    from .main import main
    from .auth import auth
    from .manager import manager
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(manager)
    configure_uploads(app, photos)
    patch_request_class(app)
    from .models import Message, User, Post, Praise, Comment, Collection
    app.add_template_global(Message, 'Message')
    app.add_template_global(User, 'User')
    app.add_template_global(Post, 'Post')
    app.add_template_global(Comment, 'Comment')
    return app
