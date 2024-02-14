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
    'docassemble==1.4.96',
    "3to2==1.1.1",
    "aiohttp==3.9.1",
    "aiohttp-retry==2.8.3",
    "aiosignal==1.3.1",
    "alembic==1.13.1",
    "anyio==4.2.0",
    "astunparse==1.6.3",
    "async-timeout==4.0.3",
    "atomicwrites==1.4.1",
    "attrs==23.1.0",
    "azure-common==1.1.28",
    "azure-core==1.29.6",
    "azure-identity==1.15.0",
    "azure-keyvault-secrets==4.7.0",
    "azure-nspkg==3.0.2",
    "azure-storage-blob==12.19.0",
    "Babel==2.14.0",
    "bcrypt==4.1.2",
    "beautifulsoup4==4.12.2",
    "bleach==6.1.0",
    "blinker==1.7.0",
    "boto==2.49.0",
    "boto3==1.34.5",
    "botocore==1.34.5",
    "cachetools==5.3.2",
    "cairocffi==1.6.1",
    "CairoSVG==2.7.1",
    "certifi==2023.11.17",
    "cffi==1.16.0",
    "chardet==5.2.0",
    "charset-normalizer==3.3.2",
    "click==8.1.7",
    "colorama==0.4.6",
    "commonmark==0.9.1",
    "convertapi==1.7.0",
    "cryptography==41.0.7",
    "cssselect2==0.7.0",
    "defusedxml==0.7.1",
    "Deprecated==1.2.14",
    "deprecation==2.1.0",
    "docassemble-backports==1.0",
    "Docassemble-Pattern==3.6.7",
    "docassemble-textstat==0.7.2",
    "docopt==0.6.2",
    "docutils==0.20.1",
    "docxcompose==1.4.0",
    "docxtpl==0.16.7",
    "et-xmlfile==1.1.0",
    "exceptiongroup==1.2.0",
    "Flask==3.0.0",
    "Flask-Mail==0.9.1",
    "frozenlist==1.4.1",
    "future==0.18.3",
    "geographiclib==2.0",
    "geopy==2.4.1",
    "google-api-core==2.15.0",
    "google-api-python-client==2.111.0",
    "google-auth==2.25.2",
    "google-auth-httplib2==0.2.0",
    "google-auth-oauthlib==1.2.0",
    "google-cloud-core==2.4.1",
    "google-cloud-storage==2.14.0",
    "google-cloud-vision==3.5.0",
    "google-crc32c==1.5.0",
    "google-i18n-address==3.1.0",
    "google-resumable-media==2.7.0",
    "googleapis-common-protos==1.62.0",
    "greenlet==3.0.2",
    "grpcio==1.60.0",
    "grpcio-status==1.60.0",
    "guess-language-spirit==0.5.3",
    "httplib2==0.22.0",
    "Hyphenate==1.1.0",
    "idna==3.6",
    "img2pdf==0.5.1",
    "importlib-metadata==7.0.0",
    "importlib-resources==6.1.1",
    "iniconfig==2.0.0",
    "isodate==0.6.1",
    "itsdangerous==2.1.2",
    "jaraco.classes==3.3.0",
    "jdcal==1.4.1",
    "jeepney==0.8.0",
    "jellyfish==0.11.2",
    "Jinja2==3.1.3",
    "jmespath==1.0.1",
    "joblib==1.3.2",
    "keyring==24.3.0",
    "lxml==4.9.4",
    "Mako==1.3.0",
    "Markdown==3.5.1",
    "markdown-it-py==3.0.0",
    "MarkupSafe==2.1.3",
    "mdurl==0.1.2",
    "more-itertools==10.1.0",
    "msal==1.26.0",
    "msal-extensions==1.1.0",
    "msrest==0.7.1",
    "multidict==6.0.4",
    "namedentities==1.9.4",
    "nh3==0.2.15",
    "nltk==3.8.1",
    "num2words==0.5.13",
    "numpy==1.26.2",
    "oauth2client==4.1.3",
    "oauthlib==3.2.2",
    "openpyxl==3.1.2",
    "ordered-set==4.1.0",
    "packaging==23.2",
    "pandas==2.1.4",
    "passlib==1.7.4",
    "pdfminer.six==20221105",
    "phonenumbers==8.13.27",
    "pikepdf==8.10.1",
    "Pillow==10.1.0",
    "pkginfo==1.9.6",
    "pluggy==1.3.0",
    "ply==3.11",
    "portalocker==2.8.2",
    "proto-plus==1.23.0",
    "protobuf==4.25.1",
    "pyasn1==0.5.1",
    "pyasn1-modules==0.3.0",
    "pycountry==23.12.11",
    "pycparser==2.21",
    "pycryptodome==3.19.1",
    "pycryptodomex==3.19.1",
    "pycurl==7.45.2",
    "Pygments==2.17.2",
    "PyJWT==2.8.0",
    "PyLaTeX==1.4.2",
    "pyparsing==3.1.1",
    "pypng==0.20220715.0",
    "pytest==7.4.3",
    "python-dateutil==2.8.2",
    "python-docx==1.1.0",
    "python-editor==1.0.4",
    "pytz==2023.3.post1",
    "pytz-deprecation-shim==0.1.0.post0",
    "PyYAML==6.0.1",
    "pyzbar==0.1.9",
    "qrcode==7.4.2",
    "readme-renderer==42.0",
    "regex==2023.10.3",
    "reportlab==4.0.8",
    "repoze.lru==0.7",
    "requests==2.31.0",
    "requests-oauthlib==1.3.1",
    "requests-toolbelt==1.0.0",
    "rfc3986==2.0.0",
    "rich==13.7.0",
    "rsa==4.7.2",
    "ruamel.yaml==0.18.5",
    "ruamel.yaml.bytes==0.1.0",
    "ruamel.yaml.clib==0.2.8",
    "ruamel.yaml.string==0.1.1",
    "s3transfer==0.9.0",
    "scipy==1.11.4",
    "SecretStorage==3.3.3",
    "six==1.16.0",
    "sniffio==1.3.0",
    "sortedcontainers==2.4.0",
    "soupsieve==2.5",
    "SQLAlchemy==2.0.23",
    "tinycss2==1.2.1",
    "titlecase==2.4.1",
    "toml==0.10.2",
    "tomli==2.0.1",
    "tqdm==4.66.1",
    "twilio==8.11.0",
    "twine==4.0.2",
    "typing_extensions==4.9.0",
    "tzdata==2023.3",
    "tzlocal==5.2",
    "ua-parser==0.18.0",
    "uritemplate==4.1.1",
    "urllib3==2.0.7",
    "us==3.1.1",
    "user-agents==2.2.0",
    "wcwidth==0.2.12",
    "webencodings==0.5.1",
    "Werkzeug==3.0.1",
    "wrapt==1.16.0",
    "xfdfgen==0.4",
    "xlrd==2.0.1",
    "XlsxWriter==3.1.9",
    "xlwt==1.3.0",
    "yarl==1.9.4",
    "zipp==3.17.0"
]

setup(name='docassemble.base',
      version='1.4.96',
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
