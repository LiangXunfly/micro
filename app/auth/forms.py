# -*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    check_password = PasswordField('check_password', validators=[DataRequired(),
                                                                EqualTo('password',
                                                                message='password must match')])
    register = SubmitField('register')


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    login = SubmitField('login')