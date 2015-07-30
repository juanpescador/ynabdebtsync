# -*- coding: utf8 -*-

from . import api
from flask import render_template

@api.flask_app.route('/')
def index():
    return render_template('index.html')
