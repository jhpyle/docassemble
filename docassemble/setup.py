import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='docassemble',
      version='0.4.58',
      description=('The namespace package for the docassemble system.'),
      long_description=read("README.md"),
      long_description_content_type='text/markdown',
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='https://docassemble.org',
      download_url='https://download.docassemble.org/docassemble.tar.gz',
      packages=find_packages(),
      zip_safe = False,
     )
