# -*- coding: UTF-8 -*-
from . import auth
from .forms import RegisterForm, LoginForm
from ..models import User
from .. import db
from flask import flash, redirect, render_template, url_for, request
from flask_login import login_user, logout_user


@auth.route('/register', methods=['post', 'get'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()
        if user is None:
            # user = User(username=username, password=form.password.data)
            user = User()
            user.username = username
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
        else:
            flash('The username has been registered')
            return redirect(url_for('register.html', form=form))
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['post', 'get'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('username or password invalid')
            return redirect('auth.login')
        login_user(user)
        if user.type == 0 or user.type is None:
            return redirect(request.args.get('next') or url_for('main.index'))
        elif user.type == 1:
            return redirect(url_for('manager.undealed_reports'))
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('You logout!')
    return redirect(url_for('main.index'))
