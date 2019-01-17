import os
from wtforms import *
from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'flaskkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
# app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME'] = '18668167812@163.com'
app.config['MAIL_PASSWORD'] = 'ferrari1'
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin<18668167812@163.com>'
app.config['FLASKY_ADMIN'] = '405701984@qq.com'

boot = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
mail = Mail(app)


@app.route('/')
def index():
    # user_agent=request.headers.get('user-agent')
    return render_template('index.html', current_time=datetime.utcnow())


@app.route('/userr/', methods=['GET', 'POST'])
@app.route('/userr/<name>', methods=['GET', 'POST'])
def userr(name=None):
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
                if app.config['FLASKY_ADMIN']:
                    send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
            else:
                session['known'] = True
        session['name'] = form.name.data
        session['retext'] = form.texts.data
        return redirect(url_for('userr', name=session.get('name')))
    return render_template('user.html', form=form, name=session.get('name'), comments=lt, retext=session.get('retext'),
                           known=session.get('known', False))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


class NameForm(FlaskForm):
    name = StringField('what is your name?', validators=[validators.DataRequired()])
    texts = TextAreaField()
    submit = SubmitField('Submit')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, templete, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(templete + '.txt', **kwargs)
    msg.html = render_template(templete + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
