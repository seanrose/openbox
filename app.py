import os
import requests
import simplejson as json
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def openbox():
    return render_template('openbox.html')


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

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
