# -*- coding: utf8 -*-


from server import flask_app
from flask import render_template, session, request, redirect, url_for
import urllib

@flask_app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        session['dropbox_token'] = request.form['other_target_category']
        return redirect(url_for('index'))
    return render_template('index.html')


@flask_app.route('/dropboxauth', methods=['GET'])
def dropbox_auth():
    params = {'response_type': 'token', 'client_id': 'uo6kvpwo8rv9bqi',
                'redirect_uri': 'http://localhost:5000'}
    url = 'https://www.dropbox.com/1/oauth2/authorize'
    return redirect(url + '?' + urllib.urlencode(params))

flask_app.secret_key = 'secret key'
