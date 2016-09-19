"""
demo Oauth2 service utilizing rauth connected to a cf-uaa docker backend
"""

import os
import flask
from flask import Flask, redirect, url_for, session, Response
from rauth import OAuth2Service
import random, string
import json

app = flask.Flask(__name__)
# you can specify the consumer key and consumer secret in the application,
#   like this:

app.config.update(
    SECRET_KEY='uaa',
    DEBUG=True
)

uaa = OAuth2Service(
    client_id='flask-rauth',
    client_secret='uaa_demo',
    name='flask-rauth',
    authorize_url='http://172.17.0.114:8080/oauth/authorize',
    access_token_url='http://172.17.0.114:8080/oauth/token',
    base_url='http://172.17.0.114:8080')

s = string.lowercase + string.uppercase


# the Rauth service detects the consumer_key and consumer_secret using
#   `current_app`.
# def test_connection(self):
#    with app.app_context():

@app.route('/')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    userinfo = access_token

    # from pprint import pformat
    # return Response(pformat(userinfo.content), mimetype='text/plain')
    return 'It worked ! %s' % userinfo


@app.route('/login')
def login():
    flask.session["state"] = ''.join(random.sample(s, 12))
    redirect_uri = 'http://127.0.0.1:5000/authorized'
    params = {'scope': 'openid+uaa.user',
              'response_type': 'code',
              'state': flask.session["state"],
              'redirect_uri': redirect_uri}
    url = uaa.get_authorize_url(**params)
    return flask.redirect(url)


@app.route('/authorized')
def callback():
    auth = uaa.get_auth_session(data={'code': flask.request.args.get('code'),
                                      'grant_type': 'authorization_code',
                                      'state': flask.request.args.get('state'),
                                      'redirect_uri': 'http://127.0.0.1:5000/authorized'}, decoder=json.loads)

    session['access_token'] = auth.access_token

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
