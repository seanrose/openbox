import os
import requests
import simplejson as json

from flask import Flask, request, render_template, redirect, session, url_for
from datetime import datetime, timedelta
from functools import wraps
from flask.ext.wtf import Form
# from settings import SECRET_KEY, CLIENT_ID, CLIENT_SECRET

SECRET_KEY = os.environ.get('SECRET_KEY')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
box_auth = 'https://api.box.com/oauth2/authorize?client_id={}&response_type=code'.format(CLIENT_ID)

app = Flask(__name__)


def requires_auth(func):
    """Checks for OAuth credentials in the session"""
    @wraps(func)
    def checked_auth(*args, **kwargs):
        if 'oauth_credentials' not in session:
            return redirect(box_auth)
        else:
            return func(*args, **kwargs)
    return checked_auth


def refresh_access_token_if_needed(func):
    """
    Checks to see if the OAuth credentials are expired based
    on what we know about the last access token we got
    and if so refreshes the access_token
    """
    @wraps(func)
    def checked_auth(*args, **kwargs):
        if oauth_credentials_are_expired():
            refresh_oauth_credentials()

        return func(*args, **kwargs)

    return checked_auth


@app.route('/')
@requires_auth
def openbox():
    form = Form()
    return render_template('openbox.html', form=form)


@app.route('/box_auth')
def box_auth():
    oauth_response = get_token(code=request.args.get('code'))
    set_oauth_credentials(oauth_response)
    return redirect(url_for('openbox'))


@app.route('/make-api-call', methods=['POST'])
def make_api_call():
    box_api_url = 'https://api.box.com/2.0'
    url = '{}{}'.format(box_api_url, request.form.get('url'))
    body = request.form.get('body')
    method = request.form.get('method')
    access_token = request.form.get('access_token')

    headers = {'Authorization': '{}{}'.format('Bearer ', access_token)}

    if method == 'POST':
        r = requests.post(url, body, headers=headers)
    elif method == 'PUT':
        r = requests.put(url, body, headers=headers)
    elif method == 'GET':
        r = requests.get(url, headers=headers)
    elif method == 'DELETE':
        r = requests.delete(url, headers=headers)
    elif method == 'OPTIONS':
        r = requests.options(url, headers=headers)

    try:
        response_json = json.dumps(r.json(), sort_keys=True, indent=4 * ' ')
    except:
        response_json = json.dumps({'no json': 'winter is coming'},
                                   sort_keys=True, indent=4 * ' ')

    return json.dumps({
        'json': response_json,
        'status': r.status_code,
        'headers': json.dumps(r.headers, sort_keys=True, indent=4 * ' ')
    })

# OAuth 2 Methods


def oauth_credentials_are_expired():
    return datetime.now() > session['oauth_expiration']


def refresh_oauth_credentials():
    """
    Gets a new access token using the refresh token grant type
    """
    refresh_token = session['oauth_credentials']['refresh_token']
    oauth_response = get_token(grant_type='refresh_token',
                               refresh_token=refresh_token)
    set_oauth_credentials(oauth_response)


def set_oauth_credentials(oauth_response):
    """
    Sets the OAuth access/refresh tokens in the session,
    along with when the access token will expire

    Will include a 15 second buffer on the exipration time
    to account for any network slowness.
    """
    token_expiration = oauth_response.get('expires_in')
    session['oauth_expiration'] = (datetime.now()
                                   + timedelta(seconds=token_expiration - 15))
    session['oauth_credentials'] = oauth_response


def get_token(**kwargs):
    """
    Used to make token requests to the Box OAuth2 Endpoint

    Args:
        grant_type
        code
        refresh_token
    """
    url = 'https://api.box.com/oauth2/token'
    if 'grant_type' not in kwargs:
        kwargs['grant_type'] = 'authorization_code'
    kwargs['client_id'] = CLIENT_ID
    kwargs['client_secret'] = CLIENT_SECRET
    token_response = requests.post(url, data=kwargs)
    return token_response.json

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.secret_key = SECRET_KEY
    app.run(host='0.0.0.0', port=port)
