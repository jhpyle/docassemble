import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', os.path.join('.', 'build'), os.path.join('.', 'dist'), 'EGG-INFO', '*.egg-info')
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
                    stack.append((fn, prefix + name + os.path.sep, package))
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

openpyxl_version = "2.5.14" if sys.version.startswith('3.5') else "3.0.0"
twine_version = "1.15.0" if sys.version.startswith('3.5') else "2.0.0"
install_requires = [
    'docassemble==1.1.54',
    "3to2==1.1.1",
    "alembic==1.2.1",
    "astunparse==1.6.2",
    "atomicwrites==1.3.0",
    "attrs==19.3.0",
    "Babel==2.7.0",
    "backports.csv==1.0.7",
    "bcrypt==3.1.7",
    "beautifulsoup4==4.8.1",
    "bleach==3.1.4",
    "blinker==1.4",
    "cachetools==3.1.1",
    "certifi==2019.9.11",
    "cffi==1.13.1",
    "chardet==3.0.4",
    "cheroot==8.2.1",
    "CherryPy==18.3.0",
    "convertapi==1.1.0",
    "docutils==0.15.2",
    "docxcompose==1.0.2",
    "docxtpl==0.10.0",
    "et-xmlfile==1.0.1",
    "fdfgen==0.16.1",
    "feedparser==5.2.1",
    "future==0.18.1",
    "geographiclib==1.50",
    "geopy==1.20.0",
    "google-api-python-client==1.7.11",
    "google-auth==1.6.3",
    "google-auth-httplib2==0.0.3",
    "google-auth-oauthlib==0.4.1",
    "google-i18n-address==2.3.5",
    "guess-language-spirit==0.5.3",
    "httplib2==0.18.0",
    "idna==2.8",
    "importlib-metadata==0.23",
    "itsdangerous==1.1.0",
    "jaraco.functools==2.0",
    "jdcal==1.4.1",
    "jellyfish==0.5.6",
    "Jinja2==2.10.3",
    "lxml==4.4.1",
    "Mako==1.1.0",
    "Markdown==3.1.1",
    "MarkupSafe==1.1.1",
    "mdx-smartypants==1.5.1",
    "more-itertools==7.2.0",
    "namedentities==1.5.2",
    "nltk==3.4.5",
    "numpy==1.17.3",
    "oauth2client==4.1.3",
    "openpyxl==" + openpyxl_version,
    "ordered-set==3.1.1",
    "packaging==19.2",
    "pandas==0.25.2",
    "passlib==1.7.1",
    "pathlib==1.0.1",
    "Pattern==3.6",
    "pdfminer.six==20200517",
    "phonenumbers==8.10.21",
    "Pillow==6.2.1",
    "pkginfo==1.5.0.1",
    "pluggy==0.13.0",
    "ply==3.11",
    "portend==2.5",
    "py==1.8.0",
    "pyasn1==0.4.7",
    "pyasn1-modules==0.2.7",
    "pycountry==19.8.18",
    "pycparser==2.19",
    "pycryptodome==3.9.0",
    "pycryptodomex==3.9.0",
    "pycurl==7.43.0.3",
    "Pygments==2.4.2",
    "PyJWT==1.7.1",
    "PyLaTeX==1.3.1",
    "pyparsing==2.4.2",
    "pyPdf==1.13",
    "PyPDF2==1.26.0",
    "pypdftk==0.4",
    "Pyphen==0.9.5",
    "pypng==0.0.20",
    "pytest==5.2.2",
    "python-dateutil==2.8.0",
    "python-docx==0.8.10",
    "python-editor==1.0.4",
    "pytz==2019.3",
    "PyYAML==5.1.2",
    "pyzbar==0.1.8",
    "qrcode==6.1",
    "readme-renderer==24.0",
    "repoze.lru==0.7",
    "requests==2.22.0",
    "requests-toolbelt==0.9.1",
    "rsa==4.0",
    "ruamel.yaml==0.16.5",
    "ruamel.yaml.clib==0.2.0",
    "scipy==1.3.1",
    "six==1.12.0",
    "sortedcontainers==2.1.0",
    "soupsieve==1.9.4",
    "SQLAlchemy==1.3.10",
    "tempora==1.14.1",
    "textstat==0.5.6",
    "titlecase==0.12.0",
    "tqdm==4.36.1",
    "twilio==6.32.0",
    "twine==" + twine_version,
    "tzlocal==2.0.0",
    "ua-parser==0.8.0",
    "uritemplate==3.0.0",
    "urllib3==1.25.6",
    "us==1.0.0",
    "user-agents==2.1",
    "wcwidth==0.1.7",
    "webencodings==0.5.1",
    "Werkzeug==1.0.0",
    "xlrd==1.2.0",
    "XlsxWriter==1.2.2",
    "xlwt==1.3.0",
    "zc.lockfile==2.0",
    "zipp==0.6.0"
]

setup(name='docassemble.base',
      version='1.1.54',
      python_requires='>=3.5',
      description=('The base components of the docassemble system.'),
      long_description=read("README.md"),
      long_description_content_type='text/markdown',
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='https://docassemble.org',
      namespace_packages = ['docassemble'],
      install_requires = install_requires,
      packages=find_packages(),
      zip_safe = False,
      package_data=find_package_data(where=os.path.join('docassemble', 'base', ''), package='docassemble.base'),
     )
