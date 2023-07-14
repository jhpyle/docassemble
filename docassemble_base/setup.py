import os
import sys
from fnmatch import fnmatchcase
from distutils.util import convert_path
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

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
                    if (fnmatchcase(name, pattern) or fn.lower() == pattern.lower()):
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
                    if (fnmatchcase(name, pattern) or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

install_requires = [
    'docassemble==1.4.65',
    "3to2==1.1.1",
    "alembic==1.9.2",
    "astunparse==1.6.3",
    "atomicwrites==1.4.1",
    "attrs==22.2.0",
    "azure-common==1.1.28",
    "azure-core==1.26.3",
    "azure-identity==1.12.0",
    "azure-keyvault-secrets==4.6.0",
    "azure-nspkg==3.0.2",
    "azure-storage-blob==12.14.1",
    "Babel==2.11.0",
    "bcrypt==4.0.1",
    "beautifulsoup4==4.11.2",
    "bleach==6.0.0",
    "blinker==1.6.2",
    "boto==2.49.0",
    "boto3==1.26.64",
    "botocore==1.29.64",
    "cachetools==5.3.0",
    "cairocffi==1.4.0",
    "CairoSVG==2.7.0",
    "certifi==2022.12.7",
    "cffi==1.15.1",
    "chardet==5.1.0",
    "charset-normalizer==3.0.1",
    "click==8.1.3",
    "colorama==0.4.6",
    "commonmark==0.9.1",
    "convertapi==1.5.0",
    "cryptography==39.0.1",
    "cssselect2==0.7.0",
    "defusedxml==0.7.1",
    "deprecation==2.1.0",
    "Docassemble-Pattern==3.6.6",
    "docassemble-textstat==0.7.2",
    "docopt==0.6.2",
    "docutils==0.19",
    "docxcompose==1.4.0",
    "docxtpl==0.16.6",
    "et-xmlfile==1.1.0",
    "exceptiongroup==1.1.0",
    "Flask==2.3.2",
    "Flask-Mail==0.9.1",
    "future==0.18.3",
    "geographiclib==2.0",
    "geopy==2.3.0",
    "google-api-core==2.11.0",
    "google-api-python-client==2.76.0",
    "google-auth==2.16.0",
    "google-auth-httplib2==0.1.0",
    "google-auth-oauthlib==0.8.0",
    "google-cloud-core==2.3.2",
    "google-cloud-storage==2.7.0",
    "google-cloud-vision==3.3.1",
    "google-crc32c==1.5.0",
    "google-i18n-address==2.5.2",
    "google-resumable-media==2.4.1",
    "googleapis-common-protos==1.58.0",
    "greenlet==2.0.2",
    "grpcio==1.53.0",
    "grpcio-status==1.51.1",
    "guess-language-spirit==0.5.3",
    "httplib2==0.21.0",
    "Hyphenate==1.1.0",
    "idna==3.4",
    "img2pdf==0.4.4",
    "importlib-metadata==6.0.0",
    "importlib-resources==5.10.2",
    "iniconfig==2.0.0",
    "isodate==0.6.1",
    "itsdangerous==2.1.2",
    "jaraco.classes==3.2.3",
    "jdcal==1.4.1",
    "jeepney==0.8.0",
    "jellyfish==0.6.1",
    "Jinja2==3.1.2",
    "jmespath==1.0.1",
    "joblib==1.2.0",
    "keyring==23.13.1",
    "lxml==4.9.2",
    "Mako==1.2.4",
    "Markdown==3.3.6",
    "markdown-it-py==2.2.0",
    "MarkupSafe==2.1.2",
    "mdurl==0.1.2",
    "mdx-smartypants==1.5.1",
    "more-itertools==9.0.0",
    "msal==1.21.0",
    "msal-extensions==1.0.0",
    "msrest==0.7.1",
    "namedentities==1.5.2",
    "nltk==3.8.1",
    "num2words==0.5.12",
    "numpy==1.24.1",
    "oauth2client==4.1.3",
    "oauthlib==3.2.2",
    "openpyxl==3.1.0",
    "ordered-set==4.1.0",
    "packaging==23.0",
    "pandas==1.5.3",
    "passlib==1.7.4",
    "pdfminer.six==20221105",
    "phonenumbers==8.13.5",
    "pikepdf==7.2.0",
    "Pillow==9.4.0",
    "pkginfo==1.9.6",
    "pluggy==1.0.0",
    "ply==3.11",
    "portalocker==2.7.0",
    "proto-plus==1.22.2",
    "protobuf==4.21.12",
    "pyasn1==0.4.8",
    "pyasn1-modules==0.2.8",
    "pycountry==22.3.5",
    "pycparser==2.21",
    "pycryptodome==3.17",
    "pycryptodomex==3.17",
    "pycurl==7.45.2",
    "Pygments==2.14.0",
    "PyJWT==2.6.0",
    "PyLaTeX==1.4.1",
    "pyparsing==3.0.9",
    "pypng==0.20220715.0",
    "pytest==7.2.1",
    "python-dateutil==2.8.2",
    "python-docx==0.8.11",
    "python-editor==1.0.4",
    "pytz==2022.7.1",
    "pytz-deprecation-shim==0.1.0.post0",
    "PyYAML==6.0",
    "pyzbar==0.1.9",
    "qrcode==7.4.1",
    "readme-renderer==37.3",
    "regex==2022.10.31",
    "reportlab==3.6.13",
    "repoze.lru==0.7",
    "requests==2.31.0",
    "requests-oauthlib==1.3.1",
    "requests-toolbelt==0.10.1",
    "rfc3986==2.0.0",
    "rich==13.3.1",
    "rsa==4.9",
    "ruamel.yaml==0.17.21",
    "ruamel.yaml.clib==0.2.7",
    "s3transfer==0.6.0",
    "scipy==1.10.0",
    "SecretStorage==3.3.3",
    "six==1.16.0",
    "sortedcontainers==2.4.0",
    "soupsieve==2.3.2.post1",
    "SQLAlchemy==2.0.1",
    "tinycss2==1.2.1",
    "titlecase==2.4",
    "toml==0.10.2",
    "tomli==2.0.1",
    "tqdm==4.64.1",
    "twilio==7.16.2",
    "twine==4.0.2",
    "typing_extensions==4.4.0",
    "tzdata==2022.7",
    "tzlocal==4.2",
    "ua-parser==0.16.1",
    "uritemplate==4.1.1",
    "urllib3==1.26.14",
    "us==2.0.2",
    "user-agents==2.2.0",
    "wcwidth==0.2.6",
    "webencodings==0.5.1",
    "Werkzeug==2.3.3",
    "xfdfgen==0.4",
    "xlrd==2.0.1",
    "XlsxWriter==3.0.8",
    "xlwt==1.3.0",
    "zipp==3.12.0",
]

if sys.version_info < (3, 9):
    install_requires.append("backports.zoneinfo==0.2.1")
else:
    install_requires.append("docassemble-backports==1.0")

setup(name='docassemble.base',
      version='1.4.65',
      python_requires='>=3.9',
      description=('The base components of the docassemble system.'),
      long_description=read("README.md"),
      long_description_content_type='text/markdown',
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='https://docassemble.org',
      namespace_packages=['docassemble'],
      install_requires=install_requires,
      packages=find_packages(),
      zip_safe=False,
      package_data=find_package_data(where=os.path.join('docassemble', 'base', ''), package='docassemble.base'),
      )
