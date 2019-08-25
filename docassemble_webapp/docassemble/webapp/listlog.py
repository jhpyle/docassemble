import os
import subprocess

from flask import Flask
app = Flask(__name__)

LOG_DIRECTORY = '/var/www/html/log'

@app.route('/listlog')
def list_log_files():
    result = subprocess.call("supervisorctl --serverurl http://localhost:9001 start sync > /dev/null && while supervisorctl --serverurl http://localhost:9001 status sync | grep -q RUNNING; do sleep 1; done", shell=True)
    if result == 0:
        return "\n".join(sorted([f for f in os.listdir(LOG_DIRECTORY) if os.path.isfile(os.path.join(LOG_DIRECTORY, f))]))
    else:
        return "There was an error."
