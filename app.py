import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
OAUTH_URL = 'https://api.box.com/oauth2'


@app.route('/')
def openbox():
    if not request.args.get('access_token'):
        return redirect(
            '{}/authorize?response_type=code&client_id={}'.format(OAUTH_URL,
                                                                  CLIENT_ID)
        )
    return render_template('openbox.html')


@app.route('/box_auth')
def box_auth():
    auth_code = request.args.get('code')

    if not auth_code:
        return jsonify({'Ned Stark': 'Winter is Coming'}), 400

    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    resp = requests.post('{}/token'.format(OAUTH_URL), data=data)

    resp_json = resp.json()

    return redirect(url_for('openbox',
                            access_token=resp_json.get('access_token'),
                            refresh_token=resp_json.get('refresh_token')))


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = False
    app.run(host='0.0.0.0', port=port)
