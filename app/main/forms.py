#!/usr/bin/env python
from flask_wtf import FlaskForm
from wtforms import *

class NameForm(FlaskForm):
    name = StringField('what is your name?', validators=[validators.DataRequired()])
    texts = TextAreaField()
    submit = SubmitField('Submit')