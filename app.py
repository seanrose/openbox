import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')


@app.route('/')
def openbox():
    return render_template('openbox.html')


@app.route('/box_auth')
def box_auth():
    auth_code = request.form.get('code')

    if not auth_code:
        return jsonify({'Ned Stark': 'Winter is Coming'}), 400

    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    resp = requests.post('https://api.box.com/oauth2/token', data=data)

    resp_json = resp.json()

    return redirect(url_for('openbox'),
                    access_token=resp_json.get('access_token'),
                    refresh_token=resp_json.get('refresh_token'))


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
