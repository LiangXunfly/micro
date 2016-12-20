# -*- coding: UTF-8 -*-

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_moment import Moment
# from app.models import User
# this would cause a cannot import


app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['POSTS_PER_PAGE'] = 3
# basedir = os.path.abspath(__file__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

db = SQLAlchemy(app)

from app import views

bootstrap = Bootstrap(app)

moment = Moment(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


from app.models import User


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
