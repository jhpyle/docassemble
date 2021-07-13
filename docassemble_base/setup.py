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
    'docassemble==1.2.90',
    "3to2==1.1.1",
    "alembic==1.6.2",
    "astunparse==1.6.3",
    "atomicwrites==1.4.0",
    "attrs==21.2.0",
    "azure-common==1.1.27",
    "azure-core==1.13.0",
    "azure-identity==1.5.0",
    "azure-keyvault-secrets==4.2.0",
    "Babel==2.9.1",
    "bcrypt==3.2.0",
    "beautifulsoup4==4.9.3",
    "bleach==3.3.0",
    "blinker==1.4",
    "cachetools==4.2.2",
    "certifi==2020.12.5",
    "cffi==1.14.5",
    "chardet==4.0.0",
    "click==7.1.2",
    "colorama==0.4.4",
    "convertapi==1.4.0",
    "cryptography==3.4.7",
    "da-pkg-resources==0.0.1",
    "Docassemble-Pattern==3.6.2",
    "docassemble-textstat==0.7.1",
    "docopt==0.6.2",
    "docutils==0.17.1",
    "docxcompose==1.3.2",
    "docxtpl==0.11.5",
    "et-xmlfile==1.1.0",
    "future==0.18.2",
    "geographiclib==1.50",
    "geopy==2.1.0",
    "google-api-core==1.26.3",
    "google-api-python-client==2.3.0",
    "google-auth-httplib2==0.1.0",
    "google-auth-oauthlib==0.4.4",
    "google-auth==1.30.0",
    "google-i18n-address==2.4.0",
    "googleapis-common-protos==1.53.0",
    "greenlet==1.1.0",
    "guess-language-spirit==0.5.3",
    "httplib2==0.19.1",
    "Hyphenate==1.1.0",
    "idna==2.10",
    "importlib-metadata==4.0.1",
    "importlib-resources==5.1.2",
    "iniconfig==1.1.1",
    "itsdangerous==2.0.0",
    "jdcal==1.4.1",
    "jeepney==0.6.0",
    "jellyfish==0.6.1",
    "Jinja2==3.0.0",
    "joblib==1.0.1",
    "keyring==23.0.1",
    "lxml==4.6.3",
    "Mako==1.1.4",
    "Marisol==0.3.0",
    "Markdown==3.3.4",
    "MarkupSafe==2.0.0",
    "mdx-smartypants==1.5.1",
    "namedentities==1.5.2",
    "nltk==3.5",
    "num2words==0.5.10",
    "numpy==1.19.4",
    "oauth2client==4.1.3",
    "oauthlib==3.1.0",
    "openpyxl==3.0.7",
    "ordered-set==4.0.2",
    "packaging==20.9",
    "pandas==1.2.4",
    "passlib==1.7.4",
    "pathlib==1.0.1",
    "pdfminer.six==20201018",
    "phonenumbers==8.12.22",
    "Pillow==8.2.0",
    "pip==20.1.1",
    "pkginfo==1.7.0",
    "pluggy==0.13.1",
    "ply==3.11",
    "protobuf==3.16.0",
    "py==1.10.0",
    "pyasn1-modules==0.2.8",
    "pyasn1==0.4.8",
    "pycountry==20.7.3",
    "pycparser==2.20",
    "pycryptodome==3.10.1",
    "pycryptodomex==3.10.1",
    "pycurl==7.43.0.6",
    "Pygments==2.9.0",
    "PyJWT==1.7.1",
    "PyLaTeX==1.4.1",
    "pyparsing==2.4.7",
    "PyPDF2==1.26.0",
    "pyPdf==1.13",
    "pypdftk==0.5",
    "pypng==0.0.20",
    "pytest==6.2.4",
    "python-dateutil==2.8.1",
    "python-docx==0.8.10",
    "python-editor==1.0.4",
    "pytz==2021.1",
    "PyYAML==5.4.1",
    "pyzbar==0.1.8",
    "qrcode==6.1",
    "readme-renderer==29.0",
    "regex==2021.4.4",
    "reportlab==3.3.0",
    "repoze.lru==0.7",
    "requests-oauthlib==1.3.0",
    "requests-toolbelt==0.9.1",
    "requests==2.25.1",
    "rfc3986==1.5.0",
    "rsa==4.7.2",
    "ruamel.yaml.clib==0.2.2",
    "ruamel.yaml==0.17.4",
    "scipy==1.5.4",
    "SecretStorage==3.3.1",
    "six==1.16.0",
    "sortedcontainers==2.3.0",
    "soupsieve==2.2.1",
    "SQLAlchemy==1.4.15",
    "titlecase==2.0.0",
    "toml==0.10.2",
    "tqdm==4.60.0",
    "twilio==6.58.0",
    "twine==3.4.1",
    "tzlocal==2.1",
    "ua-parser==0.10.0",
    "uritemplate==3.0.1",
    "urllib3==1.26.5",
    "us==2.0.2",
    "user-agents==2.2.0",
    "wcwidth==0.2.5",
    "webencodings==0.5.1",
    "Werkzeug==2.0.0",
    "xfdfgen==0.4",
    "xlrd==2.0.1",
    "XlsxWriter==1.4.3",
    "xlwt==1.3.0",
    "zipp==3.4.1"
]

setup(name='docassemble.base',
      version='1.2.90',
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
