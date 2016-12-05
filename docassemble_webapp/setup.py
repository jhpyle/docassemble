#!/usr/bin/env python

import os
from setuptools import setup, find_packages
setup(name='docassemble.webapp',
      version='0.1',
      description=('The standard web application for the docassemble system.'),
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='http://docassemble.org',
      packages=find_packages(),
      namespace_packages = ['docassemble'],
      install_requires = ['docassemble', 'docassemble.base', 'docassemble.demo', 'beautifulsoup4', 'boto', 'celery[redis]', 'eventlet', 'flask', 'flask-kvsession', 'flask-login', 'flask-mail', 'flask-sqlalchemy', 'flask-user', 'flask-wtf', 'flask-socketio', 'pip', 'psycopg2', 'python-dateutil', 'rauth', 'requests', 'wtforms', 'setuptools', 'sqlalchemy', 'tailer', 'werkzeug', 'simplekv', 'gcs-oauth2-boto-plugin', 'psutil', 'twilio', 'pycurl'],
      zip_safe = False,
      package_data={'docassemble.webapp': ['data/static/*.*', 'data/questions/*.*', 'templates/base_templates/*.html', 'templates/flask_user/*.html', 'templates/flask_user/emails/*.*', 'templates/pages/*.html', 'templates/users/*.html', 'static/app/*.*', 'static/sounds/*.*', 'static/examples/*.*', 'static/bootstrap-fileinput/img/*', 'static/bootstrap-slider/dist/*.js', 'static/bootstrap-slider/dist/css/*.css', 'static/bootstrap-fileinput/css/*.css', 'static/bootstrap-fileinput/js/*.js', 'static/bootstrap-fileinput/*.md', 'static/bootstrap/js/*.*', 'static/bootstrap/css/*.*', 'static/bootstrap/fonts/*.*', 'static/jquery-labelauty/source/*.*', 'static/jquery-labelauty/source/images/*.*', 'static/codemirror/lib/*.*', 'static/codemirror/mode/yaml/*.*', 'static/codemirror/mode/markdown/*.*', 'static/codemirror/mode/javascript/*.*', 'static/codemirror/mode/python/*.*', 'static/areyousure/*.js']},
     )
