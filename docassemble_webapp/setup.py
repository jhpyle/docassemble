#!/usr/bin/env python

import os
from setuptools import setup, find_packages
setup(name='docassemble.webapp',
      version='0.1.30',
      description=('The web application components of the docassemble system.'),
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='https://docassemble.org',
      download_url='https://download.docassemble.org/docassemble-webapp.tar.gz',
      packages=find_packages(),
      namespace_packages = ['docassemble'],
      install_requires = ['docassemble', 'docassemble.base', 'docassemble.demo', 'beautifulsoup4', 'boto', 'celery[redis]', 'eventlet', 'greenlet', 'flask', 'flask-kvsession', 'flask-login', 'flask-mail', 'flask-sqlalchemy', 'flask-user', 'flask-babel', 'flask-wtf', 'flask-socketio', 'pip', 'psycopg2', 'python-dateutil', 'rauth', 'requests', 'wtforms', 'setuptools', 'sqlalchemy', 'tailer', 'werkzeug', 'simplekv', 'gcs-oauth2-boto-plugin', 'psutil', 'twilio', 'pycurl', 'google-api-python-client', 'azure-storage', 'strict-rfc3339', 'pyotp', 'links-from-link-header'],
      zip_safe = False,
      package_data={'docassemble.webapp': ['data/*.*', 'data/static/*.*', 'data/static/favicon/*.*', 'data/questions/*.*', 'templates/base_templates/*.html', 'templates/flask_user/*.html', 'templates/flask_user/emails/*.*', 'templates/pages/*.html', 'templates/users/*.html', 'static/app/*.*', 'static/sounds/*.*', 'static/examples/*.*', 'static/bootstrap-fileinput/img/*', 'static/bootstrap-slider/dist/*.js', 'static/bootstrap-slider/dist/css/*.css', 'static/bootstrap-fileinput/css/*.css', 'static/bootstrap-fileinput/js/*.js', 'static/bootstrap-fileinput/*.md', 'static/bootstrap/js/*.*', 'static/bootstrap/css/*.*', 'static/bootstrap/fonts/*.*', 'static/labelauty/source/*.*', 'static/labelauty/source/images/*.*', 'static/codemirror/lib/*.*', 'static/codemirror/addon/search/*.*', 'static/codemirror/addon/scroll/*.*', 'static/codemirror/addon/dialog/*.*', 'static/codemirror/addon/edit/*.*', 'static/codemirror/addon/hint/*.*', 'static/codemirror/mode/yaml/*.*', 'static/codemirror/mode/markdown/*.*', 'static/codemirror/mode/javascript/*.*', 'static/codemirror/mode/css/*.*', 'static/codemirror/mode/python/*.*', 'static/codemirror/keymap/*.*', 'static/areyousure/*.js']},
     )
