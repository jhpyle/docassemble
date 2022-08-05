import os
import subprocess
import time
from packaging import version

from flask import Flask, abort, make_response, render_template, request
app = Flask(__name__)

LOG_DIRECTORY = '/var/www/html/log'

version_file = '/usr/share/docassemble/webapp/VERSION'
if os.path.isfile(version_file) and os.access(version_file, os.R_OK):
    with open(version_file, 'r', encoding='utf-8') as fp:
        system_version = fp.read().strip()
else:
    system_version = '0.1.12'

if version.parse(system_version) < version.parse('1.4.0'):
    READY_FILE = '/usr/share/docassemble/webapp/ready'
else:
    READY_FILE = '/var/run/docassemble/ready'


@app.route('/listlog')
def list_log_files():
    cmd = "supervisorctl "
    if os.getenv('DASUPERVISORUSERNAME', None):
        cmd += '--username ' + os.getenv('DASUPERVISORUSERNAME') + ' --password ' + os.getenv('DASUPERVISORPASSWORD') + ' '
    cmd += "--serverurl http://localhost:9001 start sync > /dev/null && while supervisorctl --serverurl http://localhost:9001 status sync | grep -q RUNNING; do sleep 1; done"
    result = subprocess.run(cmd, shell=True, check=False).returncode
    if result == 0:
        file_listing = [f for f in os.listdir(LOG_DIRECTORY) if os.path.isfile(os.path.join(LOG_DIRECTORY, f))]
        if len(file_listing) == 0:
            time.sleep(2)
            file_listing = [f for f in os.listdir(LOG_DIRECTORY) if os.path.isfile(os.path.join(LOG_DIRECTORY, f))]
        return "\n".join(sorted(file_listing))
    return "There was an error."


@app.route("/listlog/health_check", methods=['GET'])
def health_check():
    if request.args.get('ready', False):
        if not os.path.isfile(READY_FILE):
            abort(400)
    response = make_response(render_template('pages/health_check.html', content="OK"), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response
