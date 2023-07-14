import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

setup(name='docassemble',
      version='1.4.65',
      python_requires='>=3.9',
      description=('The namespace package for the docassemble system.'),
      long_description=read("README.md"),
      long_description_content_type='text/markdown',
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='https://docassemble.org',
      packages=find_packages(),
      zip_safe=False
      )
