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
      install_requires = ['docassemble'],
      zip_safe = False,
      package_data={'docassemble.webapp': ['templates/base_templates/*.html', 'templates/flask_user/*.html', 'templates/pages/*.html', 'templates/users/*.html', 'static/app/*.*', 'static/bootstrap-fileinput/css/*.css', 'static/bootstrap-fileinput/js/*.js', 'static/bootstrap-fileinput/*.md', 'static/prettyCheckable/dist/*.*', 'static/prettyCheckable/img/*.*', 'static/prettyCheckable/dev/*.*']},
     )
