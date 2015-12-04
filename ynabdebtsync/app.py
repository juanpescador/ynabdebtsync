# -*- coding: utf8 -*-

from . import api
from flask import render_template, session, request, redirect, url_for

@api.flask_app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['dropbox_token'] = request.form['other_target_category']
        return redirect(url_for('index'))
    return render_template('index.html')

api.flask_app.secret_key = 'secret key'
