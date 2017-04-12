# -*- coding: UTF-8 -*-
from . import manager
from ..models import Report, Post, Comment, Message
from sqlalchemy import desc
from flask import render_template, flash, redirect, request, url_for
from .forms import DealReportForm
from app import db
from datetime import datetime, timedelta

types = [Post, Comment]


@manager.route('/undealed_reports')
def undealed_reports():
    undealed_reports = Report.query.filter(Report.dealed==False).order_by(desc(Report.timestamp)).all()
    return render_template('manager/undealed_reports.html', reports=undealed_reports, types=types)


@manager.route('/dealed_reports')
def dealed_reports():
    dealed_reports = Report.query.filter(Report.dealed==True).order_by(desc(Report.timestamp)).all()
    return render_template('manager/dealed_reports.html', reports=dealed_reports, types=types)


@manager.route('/deal_report/<int:id>', methods=['GET', 'POST'])
def deal_report(id):
    report = Report.query.get(id)
    if report is None:
        flash('the report id is not valid')
        return redirect(request.referrer)
    if report.type == 1:
        post = Post.query.get(report.refer_id)
        user = post.author
    elif report.type == 2:
        comment = Comment.query.get(report.refer_id)
        user = comment.author
        post = Post.query.get(comment.post_id)
    form = DealReportForm()
    if form.validate_on_submit():
        if form.submit.data:
            if form.period.data == '0':
                report.result = 0
            db.session.add(report)
            db.session.commit()
            if form.period.data == '1':
                user.valid_time = datetime.now() + timedelta(0, 10800)
                report.result = 1
            elif form.period.data == '2':
                user.valid_time = datetime.now() + timedelta(1)
                report.result = 2
            elif form.period.data == '3':
                user.valid_time = datetime.now() + timedelta(3)
                report.result = 3
            elif form.period.data == '4':
                user.valid_time = datetime.now() + timedelta(30)
                report.result = 4
            report.dealed = True
            message = Message(receive_id=user.id, refer_id=report.id, post_id=post.id, type=6)
            db.session.add(user)
            db.session.add(report)
            db.session.add(message)
            db.session.commit()
        return redirect(url_for('manager.undealed_reports'))
    return render_template('manager/deal_report.html', form=form, report=report)
