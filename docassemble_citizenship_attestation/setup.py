#!/usr/bin/env python

import os
from setuptools import setup, find_packages

setup(name='docassemble.citizenship_attestation',
      version='0.1',
      description=('A docassemble extension.'),
      author=' ',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='http://docassemble.org',
      packages=find_packages(),
      namespace_packages = ['docassemble'],
      zip_safe = False,
      package_data={'docassemble.citizenship_attestation': ['data/templates/*', 'data/questions/*', 'data/static/*']},
     )

