#!/usr/bin/env python

import os
from setuptools import setup, find_packages

setup(name='docassemble.demo',
      version='0.1',
      description=('A demonstration package for docassemble.'),
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='http://docassemble.org',
      packages=find_packages(),
      namespace_packages = ['docassemble'],
      install_requires = ['docassemble'],
      zip_safe = False,
      package_data={'docassemble.demo': ['data/templates/*', 'data/questions/*', 'data/static/*']},
     )
