#!/usr/bin/env python

import os
from setuptools import setup, find_packages

setup(name='docassemble.base',
      version='0.1',
      description=('A python module for assembling documents from templates while automatically querying a user for necessary information.'),
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='http://docassemble.org',
      namespace_packages = ['docassemble'],
      install_requires = ['docassemble'],
      packages=find_packages(),
      zip_safe = False,
      package_data={'docassemble.base': ['data/templates/*', 'data/questions/*', 'data/static/*']},
     )
