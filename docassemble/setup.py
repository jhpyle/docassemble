#!/usr/bin/env python

import os
from setuptools import setup, find_packages

setup(name='docassemble',
      version='0.1',
      description=('A python module for assembling documents from templates while automatically querying a user for necessary information.'),
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='http://docassemble.org',
      packages=find_packages(),
      zip_safe = False,
     )
