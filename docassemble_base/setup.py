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
    'docassemble==1.5.1',
    "3to2==1.1.1",
    "aiohappyeyeballs==2.3.5",
    "aiohttp==3.10.3",
    "aiohttp-retry==2.8.3",
    "aiosignal==1.3.1",
    "alembic==1.13.2",
    "anyio==4.4.0",
    "astunparse==1.6.3",
    "async-timeout==4.0.3",
    "atomicwrites==1.4.1",
    "attrs==24.2.0",
    "azure-common==1.1.28",
    "azure-core==1.30.2",
    "azure-identity==1.17.1",
    "azure-keyvault-secrets==4.8.0",
    "azure-nspkg==3.0.2",
    "azure-storage-blob==12.22.0",
    "babel==2.16.0",
    "backports.tarfile==1.2.0",
    "bcrypt==4.2.0",
    "beautifulsoup4==4.12.3",
    "bleach==6.1.0",
    "blinker==1.8.2",
    "boto==2.49.0",
    "boto3==1.34.158",
    "botocore==1.34.158",
    "cachetools==5.4.0",
    "cairocffi==1.7.1",
    "CairoSVG==2.7.1",
    "certifi==2024.7.4",
    "cffi==1.17.0",
    "chardet==5.2.0",
    "charset-normalizer==3.3.2",
    "click==8.1.7",
    "colorama==0.4.6",
    "commonmark==0.9.1",
    "convertapi==1.8.0",
    "cryptography==43.0.0",
    "cssselect2==0.7.0",
    "defusedxml==0.7.1",
    "Deprecated==1.2.14",
    "deprecation==2.1.0",
    "docassemble-backports==1.0",
    "Docassemble-Pattern==3.6.7",
    "docassemble-textstat==0.7.2",
    "docopt==0.6.2",
    "docutils==0.21.2",
    "docxcompose==1.4.0",
    "docxtpl==0.18.0",
    "et-xmlfile==1.1.0",
    "exceptiongroup==1.2.2",
    "Flask==3.0.3",
    "Flask-Mail==0.10.0",
    "frozenlist==1.4.1",
    "future==1.0.0",
    "geographiclib==2.0",
    "geopy==2.4.1",
    "google-api-core==2.19.1",
    "google-api-python-client==2.140.0",
    "google-auth==2.17.0",
    "google-auth-httplib2==0.2.0",
    "google-auth-oauthlib==1.2.1",
    "google-cloud-core==2.4.1",
    "google-cloud-storage==2.11.0",
    "google-cloud-vision==3.7.4",
    "google-crc32c==1.5.0",
    "google-i18n-address==3.1.0",
    "google-resumable-media==2.7.2",
    "googleapis-common-protos==1.63.2",
    "greenlet==3.0.3",
    "grpcio==1.65.4",
    "grpcio-status==1.65.4",
    "guess-language-spirit==0.5.3",
    "httplib2==0.22.0",
    "Hyphenate==1.1.0",
    "idna==3.7",
    "img2pdf==0.5.1",
    "importlib_metadata==8.2.0",
    "importlib_resources==6.4.0",
    "iniconfig==2.0.0",
    "isodate==0.6.1",
    "itsdangerous==2.2.0",
    "jaraco.classes==3.4.0",
    "jaraco.context==5.3.0",
    "jaraco.functools==4.0.2",
    "jdcal==1.4.1",
    "jeepney==0.8.0",
    "jellyfish==1.1.0",
    "Jinja2==3.1.4",
    "jmespath==1.0.1",
    "joblib==1.4.2",
    "keyring==25.3.0",
    "lxml==5.3.0",
    "Mako==1.3.5",
    "Markdown==3.6",
    "markdown-it-py==3.0.0",
    "MarkupSafe==2.1.5",
    "mdurl==0.1.2",
    "more-itertools==10.4.0",
    "msal==1.30.0",
    "msal-extensions==1.2.0",
    "msrest==0.7.1",
    "multidict==6.0.5",
    "namedentities==1.9.4",
    "nh3==0.2.18",
    "nltk==3.8.2",
    "num2words==0.5.13",
    "numpy==2.0.1",
    "oauth2client==4.1.3",
    "oauthlib==3.2.2",
    "openpyxl==3.1.5",
    "ordered-set==4.1.0",
    "packaging==24.1",
    "pandas==2.2.2",
    "passlib==1.7.4",
    "pdfminer.six==20240706",
    "phonenumbers==8.13.43",
    "pikepdf==9.1.1",
    "pillow==10.4.0",
    "pkginfo==1.10.0",
    "pluggy==1.5.0",
    "ply==3.11",
    "portalocker==2.10.1",
    "proto-plus==1.24.0",
    "protobuf==5.27.3",
    "pyasn1==0.6.0",
    "pyasn1_modules==0.4.0",
    "pycountry==24.6.1",
    "pycparser==2.22",
    "pycryptodome==3.20.0",
    "pycryptodomex==3.20.0",
    "pycurl==7.45.3",
    "Pygments==2.18.0",
    "PyJWT==2.9.0",
    "PyLaTeX==1.4.2",
    "pyparsing==3.1.2",
    "pypng==0.20220715.0",
    "pytest==8.3.2",
    "python-dateutil==2.9.0.post0",
    "python-docx==1.1.2",
    "python-editor==1.0.4",
    "pytz==2024.1",
    "pytz-deprecation-shim==0.1.0.post0",
    "PyYAML==6.0.2",
    "pyzbar==0.1.9",
    "qrcode==7.4.2",
    "readme_renderer==44.0",
    "regex==2024.7.24",
    "reportlab==4.2.2",
    "repoze.lru==0.7",
    "requests==2.32.3",
    "requests-oauthlib==2.0.0",
    "requests-toolbelt==1.0.0",
    "rfc3986==2.0.0",
    "rich==13.7.1",
    "rsa==4.7.2",
    "ruamel.yaml==0.18.6",
    "ruamel.yaml.bytes==0.1.0",
    "ruamel.yaml.clib==0.2.8",
    "ruamel.yaml.string==0.1.1",
    "s3transfer==0.10.2",
    "scipy==1.14.0",
    "SecretStorage==3.3.3",
    "six==1.16.0",
    "sniffio==1.3.1",
    "sortedcontainers==2.4.0",
    "soupsieve==2.5",
    "SQLAlchemy==2.0.32",
    "tinycss2==1.3.0",
    "titlecase==2.4.1",
    "toml==0.10.2",
    "tomli==2.0.1",
    "tqdm==4.66.5",
    "twilio==9.2.3",
    "twine==5.1.1",
    "typing_extensions==4.12.2",
    "tzdata==2024.1",
    "tzlocal==5.2",
    "ua-parser==0.18.0",
    "uritemplate==4.1.1",
    "urllib3==2.2.2",
    "us==3.2.0",
    "user-agents==2.2.0",
    "wcwidth==0.2.13",
    "webencodings==0.5.1",
    "Werkzeug==3.0.3",
    "wrapt==1.16.0",
    "xfdfgen==0.4",
    "xlrd==2.0.1",
    "XlsxWriter==3.2.0",
    "xlwt==1.3.0",
    "yarl==1.9.4",
    "zipp==3.20.0"
]

setup(name='docassemble.base',
      version='1.5.1',
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
