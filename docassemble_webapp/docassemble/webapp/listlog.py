import os
import subprocess

from flask import Flask, make_response, render_template
app = Flask(__name__)

LOG_DIRECTORY = '/var/www/html/log'

@app.route('/listlog')
def list_log_files():
    result = subprocess.call("supervisorctl --serverurl http://localhost:9001 start sync > /dev/null && while supervisorctl --serverurl http://localhost:9001 status sync | grep -q RUNNING; do sleep 1; done", shell=True)
    if result == 0:
        return "\n".join(sorted([f for f in os.listdir(LOG_DIRECTORY) if os.path.isfile(os.path.join(LOG_DIRECTORY, f))]))
    else:
        return "There was an error."

@app.route("/listlog/health_check", methods=['GET'])
def health_check():
    response = make_response(render_template('pages/health_check.html', content="OK"), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response
