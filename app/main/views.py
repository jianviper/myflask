#!/usr/bin/env python
from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, current_app

from . import main
from .forms import NameForm
from .. import db
from ..models import Role, User
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
def index():
    # user_agent=request.headers.get('user-agent')
    return render_template('index.html', current_time=datetime.utcnow())


@main.route('/user/', methods=['GET', 'POST'])
@main.route('/user/<name>', methods=['GET', 'POST'])
def user(name=None):
    form = NameForm()
    lt = []
    session['name'] = name
    for i in range(5):
        lt.append(i)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Look like you have changed your name!')
            if user is None:
                # user_role = Role(name='Admin')
                user = User(username=form.name.data, role_id=3)
                db.session.add(user)
                db.session.commit()
                session['known'] = False
                if current_app.config['FLASKY_ADMIN']:
                    send_email(current_app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
            else:
                session['known'] = True
        session['name'] = form.name.data
        session['retext'] = form.texts.data
        return redirect(url_for('main.user', name=session.get('name')))
    return render_template('user.html', form=form, name=session.get('name'), comments=lt, retext=session.get('retext'),
        known=session.get('known', False))


@main.route('/data_visual/', methods=['GET'])
def data_visual():
    return render_template('data_visual.html')
