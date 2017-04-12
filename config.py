# -*- coding: UTF-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'hard to guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOADED_PHOTOS_DEST = os.path.join(os.getcwd(), "app/static/images")
    WHOOSH_BASE = os.path.join(basedir, 'search.db')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    POSTS_PER_PAGE = 3
    DEFAULT_AVATAR = '/app/static/images/favicon.ico'

config = {'default' : DevelopmentConfig}