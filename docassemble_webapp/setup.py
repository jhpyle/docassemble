#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='docassemble.webapp',
      version='0.3.3',
      description=('The web application components of the docassemble system.'),
      long_description=read("README.md"),
      long_description_content_type='text/markdown',
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='https://docassemble.org',
      download_url='https://download.docassemble.org/docassemble-webapp.tar.gz',
      packages=find_packages(),
      namespace_packages = ['docassemble'],
      install_requires = ['docassemble==0.3.3', 'docassemble.base==0.3.3', 'docassemble.demo==0.3.3', 'beautifulsoup4', 'boto', 'boto3', 'celery[redis]==4.1.0', 'kombu==4.1.0', 'eventlet', 'greenlet', 'flask', 'flask-kvsession', 'flask-login', 'flask-mail', 'flask-sqlalchemy', 'flask-user<0.7', 'flask-babel', 'flask-wtf', 'flask-socketio', 'pip', 'psycopg2-binary', 'mysql-python', 'python-dateutil', 'rauth', 'requests', 'wtforms==2.1', 'setuptools', 'sqlalchemy', 'tailer', 'werkzeug', 'simplekv', 'gcs-oauth2-boto-plugin', 'psutil', 'twilio', 'pycurl', 'google-api-python-client', 'azure-storage', 'strict-rfc3339', 'pyotp', 'links-from-link-header', 'alembic', 'pandas', 'numpy', 'sklearn', 'scipy', 'gspread', 'oauth2client', 'google-auth', 'google-cloud-translate', 'google-cloud-storage', 'iso8601'],
      zip_safe = False,
      package_data={'docassemble.webapp': ['alembic.ini', 'alembic/*', 'alembic/versions/*', 'data/*.*', 'data/static/*.*', 'data/static/favicon/*.*', 'data/questions/*.*', 'templates/base_templates/*.html', 'templates/flask_user/*.html', 'templates/flask_user/emails/*.*', 'templates/pages/*.html', 'templates/pages/*.xml', 'templates/users/*.html', 'static/app/*.*', 'static/sounds/*.*', 'static/examples/*.*', 'static/fontawesome/js/*.*', 'static/fontawesome/css/*.*', 'static/office/*.*', 'static/bootstrap-fileinput/img/*', 'static/bootstrap-slider/dist/*.js', 'static/bootstrap-slider/dist/css/*.css', 'static/bootstrap-fileinput/css/*.css', 'static/bootstrap-fileinput/js/*.js', 'static/bootstrap-fileinput/themes/fa/*.js', 'static/bootstrap-fileinput/themes/fas/*.js', 'static/bootstrap-combobox/css/*.css', 'static/bootstrap-combobox/js/*.js', 'static/bootstrap-fileinput/*.md', 'static/bootstrap/js/*.*', 'static/bootstrap/css/*.*', 'static/labelauty/source/*.*', 'static/codemirror/lib/*.*', 'static/codemirror/addon/search/*.*', 'static/codemirror/addon/scroll/*.*', 'static/codemirror/addon/dialog/*.*', 'static/codemirror/addon/edit/*.*', 'static/codemirror/addon/hint/*.*', 'static/codemirror/mode/yaml/*.*', 'static/codemirror/mode/markdown/*.*', 'static/codemirror/mode/javascript/*.*', 'static/codemirror/mode/css/*.*', 'static/codemirror/mode/python/*.*', 'static/codemirror/mode/htmlmixed/*.*', 'static/codemirror/mode/xml/*.*', 'static/codemirror/keymap/*.*', 'static/areyousure/*.js', 'static/popper/*.*', 'static/popper/umd/*.*', 'static/popper/esm/*.*']},
     )
