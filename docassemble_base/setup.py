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

install_requires = [
    'docassemble==1.2.56',
    "3to2==1.1.1",
    "alembic==1.4.3",
    "astunparse==1.6.3",
    "atomicwrites==1.4.0",
    "attrs==20.3.0",
    "Babel==2.9.0",
    "bcrypt==3.2.0",
    "beautifulsoup4==4.9.3",
    "bleach==3.3.0",
    "blinker==1.4",
    "cachetools==4.1.1",
    "certifi==2020.11.8",
    "cffi==1.14.4",
    "chardet==3.0.4",
    "click==7.1.2",
    "colorama==0.4.4",
    "convertapi==1.4.0",
    "cryptography==3.3.2",
    "docopt==0.6.2",
    "docutils==0.16",
    "docxcompose==1.3.0",
    "docxtpl==0.11.2",
    "et-xmlfile==1.0.1",
    "future==0.18.2",
    "geographiclib==1.50",
    "geopy==2.0.0",
    "google-api-core==1.23.0",
    "google-api-python-client==1.12.8",
    "google-auth==1.23.0",
    "google-auth-httplib2==0.0.4",
    "google-auth-oauthlib==0.4.2",
    "google-i18n-address==2.4.0",
    "googleapis-common-protos==1.52.0",
    "guess-language-spirit==0.5.3",
    "httplib2==0.19.0",
    "hyphenate==1.1.0",
    "idna==2.10",
    "importlib-metadata==3.1.0",
    "importlib-resources==3.3.0",
    "iniconfig==1.1.1",
    "itsdangerous==1.1.0",
    "jdcal==1.4.1",
    "jeepney==0.6.0",
    "jellyfish==0.6.1",
    "Jinja2==2.11.3",
    "joblib==0.17.0",
    "keyring==21.5.0",
    "lxml==4.6.3",
    "Mako==1.1.3",
    "Marisol==0.3.0",
    "Markdown==3.3.3",
    "MarkupSafe==1.1.1",
    "mdx-smartypants==1.5.1",
    "namedentities==1.5.2",
    "nltk==3.5",
    "num2words==0.5.10",
    "numpy==1.19.4",
    "oauth2client==4.1.3",
    "oauthlib==3.1.0",
    "openpyxl==3.0.5",
    "ordered-set==4.0.2",
    "packaging==20.4",
    "pandas==1.1.4",
    "passlib==1.7.4",
    "pathlib==1.0.1",
    "Docassemble-Pattern==3.6.2",
    "pdfminer.six==20201018",
    "phonenumbers==8.12.13",
    "Pillow==8.1.1",
    "pkginfo==1.6.1",
    "pluggy==0.13.1",
    "ply==3.11",
    "protobuf==3.14.0",
    "py==1.9.0",
    "pyasn1==0.4.8",
    "pyasn1-modules==0.2.8",
    "pycountry==20.7.3",
    "pycparser==2.20",
    "pycryptodome==3.9.9",
    "pycryptodomex==3.9.9",
    "pycurl==7.43.0.6",
    "Pygments==2.7.4",
    "PyJWT==1.7.1",
    "PyLaTeX==1.4.1",
    "pyparsing==2.4.7",
    "pyPdf==1.13",
    "PyPDF2==1.26.0",
    "pypdftk==0.4",
    "pypng==0.0.20",
    "pytest==6.1.2",
    "python-dateutil==2.8.1",
    "python-docx==0.8.10",
    "python-editor==1.0.4",
    "pytz==2020.4",
    "PyYAML==5.4",
    "pyzbar==0.1.8",
    "qrcode==6.1",
    "readme-renderer==28.0",
    "regex==2020.11.13",
    "reportlab==3.3.0",
    "repoze.lru==0.7",
    "requests==2.25.0",
    "requests-oauthlib==1.3.0",
    "requests-toolbelt==0.9.1",
    "rfc3986==1.4.0",
    "rsa==4.6",
    "ruamel.yaml==0.16.12",
    "ruamel.yaml.clib==0.2.2",
    "scipy==1.5.4",
    "SecretStorage==3.3.0",
    "six==1.15.0",
    "sortedcontainers==2.3.0",
    "soupsieve==2.0.1",
    "SQLAlchemy==1.3.20",
    "docassemble-textstat==0.7.1",
    "titlecase==1.1.1",
    "toml==0.10.2",
    "tqdm==4.53.0",
    "twilio==6.48.0",
    "twine==3.2.0",
    "tzlocal==2.1",
    "ua-parser==0.10.0",
    "uritemplate==3.0.1",
    "urllib3==1.26.4",
    "us==2.0.2",
    "user-agents==2.2.0",
    "wcwidth==0.2.5",
    "webencodings==0.5.1",
    "Werkzeug==1.0.1",
    "xfdfgen==0.4",
    "xlrd==1.2.0",
    "XlsxWriter==1.3.7",
    "xlwt==1.3.0",
    "zipp==3.4.0",
]

setup(name='docassemble.base',
      version='1.2.56',
      python_requires='>=3.8',
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
