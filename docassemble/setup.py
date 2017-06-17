#!/usr/bin/env python

import os
from setuptools import setup, find_packages

setup(name='docassemble',
      version='0.1.14',
      description=('A system for assembling documents from templates while automatically querying a user for necessary information.'),
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='https://docassemble.org',
      download_url='https://download.docassemble.org/docassemble.tar.gz',
      packages=find_packages(),
      zip_safe = False,
     )
