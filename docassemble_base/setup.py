#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')
def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

setup(name='docassemble.base',
      version='0.1',
      description=('A python module for assembling documents from templates while automatically querying a user for necessary information.'),
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='http://docassemble.org',
      namespace_packages = ['docassemble'],
      install_requires = ['docassemble', '3to2', 'babel', 'bcrypt', 'blinker', 'cffi', 'guess-language-spirit', 'html2text', 'httplib2', 'itsdangerous', 'jellyfish', 'jinja2', 'mako', 'markdown', 'markupsafe', 'mdx-smartypants', 'namedentities', 'passlib', 'pillow', 'pip', 'pycparser', 'pycrypto', 'pygeocoder', 'pygments', 'pyjwt', 'pypdf', 'pyrtf-ng', 'python-dateutil', 'pytz', 'pyyaml', 'six', 'titlecase', 'us', 'wheel'],
      packages=find_packages(),
      zip_safe = False,
      package_data=find_package_data(where='docassemble/base/', package='docassemble.base'),
     )
