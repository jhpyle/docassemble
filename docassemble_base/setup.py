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
    'docassemble==1.4.29',
    "3to2==1.1.1",
    "alembic==1.7.7",
    "astunparse==1.6.3",
    "atomicwrites==1.4.1",
    "attrs==21.4.0",
    "azure-common==1.1.28",
    "azure-core==1.23.1",
    "azure-identity==1.9.0",
    "azure-keyvault-secrets==4.4.0",
    "azure-nspkg==3.0.2",
    "azure-storage-blob==12.11.0",
    "Babel==2.9.1",
    "bcrypt==3.2.0",
    "beautifulsoup4==4.11.1",
    "bleach==5.0.0",
    "blinker==1.4",
    "boto==2.49.0",
    "boto3==1.21.40",
    "botocore==1.24.40",
    "cachetools==5.0.0",
    "cairocffi==1.3.0",
    "CairoSVG==2.5.2",
    "certifi==2022.12.7",
    "cffi==1.15.0",
    "chardet==4.0.0",
    "charset-normalizer==2.0.12",
    "click==8.1.2",
    "colorama==0.4.4",
    "commonmark==0.9.1",
    "convertapi==1.4.0",
    "cryptography==36.0.2",
    "cssselect2==0.5.0",
    "da-pkg-resources==0.0.1",
    "defusedxml==0.7.1",
    "Docassemble-Pattern==3.6.5",
    "docassemble-textstat==0.7.2",
    "docopt==0.6.2",
    "docutils==0.18.1",
    "docxcompose==1.3.4",
    "docxtpl==0.16.3",
    "et-xmlfile==1.1.0",
    "Flask-Mail==0.9.1",
    "future==0.18.3",
    "geographiclib==1.52",
    "geopy==2.2.0",
    "google-api-core==2.7.2",
    "google-api-python-client==2.44.0",
    "google-auth-httplib2==0.1.0",
    "google-auth-oauthlib==0.5.1",
    "google-auth==2.6.4",
    "google-cloud-core==2.3.0",
    "google-cloud-storage==2.3.0",
    "google-cloud-vision==2.7.2",
    "google-crc32c==1.3.0",
    "google-i18n-address==2.5.0",
    "google-resumable-media==2.3.2",
    "googleapis-common-protos==1.56.0",
    "greenlet==1.1.2",
    "grpcio-status==1.44.0",
    "grpcio==1.44.0",
    "guess-language-spirit==0.5.3",
    "httplib2==0.20.4",
    "Hyphenate==1.1.0",
    "idna==3.3",
    "img2pdf==0.4.4",
    "importlib-metadata==4.11.3",
    "importlib-resources==5.7.0",
    "iniconfig==1.1.1",
    "isodate==0.6.1",
    "itsdangerous==2.1.2",
    "jdcal==1.4.1",
    "jeepney==0.8.0",
    "jellyfish==0.6.1",
    "Jinja2==3.1.1",
    "jmespath==1.0.0",
    "joblib==1.2.0",
    "keyring==23.5.0",
    "lxml==4.9.1",
    "Mako==1.2.2",
    "Markdown==3.3.6",
    "MarkupSafe==2.1.1",
    "mdx-smartypants==1.5.1",
    "msal-extensions==0.3.1",
    "msal==1.17.0",
    "msrest==0.6.21",
    "namedentities==1.5.2",
    "nltk==3.7",
    "num2words==0.5.10",
    "numpy==1.22.3",
    "oauth2client==4.1.3",
    "oauthlib==3.2.1",
    "openpyxl==3.0.9",
    "ordered-set==4.1.0",
    "packaging==21.3",
    "pandas==1.4.2",
    "passlib==1.7.4",
    "pdfminer.six==20220319",
    "phonenumbers==8.12.46",
    "Pillow==9.3.0",
    "pikepdf==6.2.4",
    "pkginfo==1.8.2",
    "pluggy==1.0.0",
    "ply==3.11",
    "portalocker==2.4.0",
    "proto-plus==1.20.3",
    "protobuf==3.20.2",
    "py==1.11.0",
    "pyasn1-modules==0.2.8",
    "pyasn1==0.4.8",
    "pycountry==22.3.5",
    "pycparser==2.21",
    "pycryptodome==3.14.1",
    "pycryptodomex==3.14.1",
    "pycurl==7.45.1",
    "Pygments==2.11.2",
    "PyJWT==2.4.0",
    "PyLaTeX==1.4.1",
    "pyparsing==3.0.8",
    "pypng==0.0.21",
    "pytest==7.1.1",
    "python-dateutil==2.8.2",
    "python-docx==0.8.11",
    "python-editor==1.0.4",
    "pytz-deprecation-shim==0.1.0.post0",
    "pytz==2022.1",
    "PyYAML==6.0",
    "pyzbar==0.1.9",
    "qrcode==7.3.1",
    "readme-renderer==34.0",
    "regex==2022.3.15",
    "reportlab==3.6.9",
    "repoze.lru==0.7",
    "requests-oauthlib==1.3.1",
    "requests-toolbelt==0.9.1",
    "requests==2.27.1",
    "rfc3986==2.0.0",
    "rich==12.2.0",
    "rsa==4.7.2",
    "ruamel.yaml.clib==0.2.6",
    "ruamel.yaml==0.17.21",
    "s3transfer==0.5.2",
    "scipy==1.8.0",
    "SecretStorage==3.3.1",
    "six==1.16.0",
    "sortedcontainers==2.4.0",
    "soupsieve==2.3.2",
    "SQLAlchemy==1.4.35",
    "tinycss2==1.1.1",
    "titlecase==2.3",
    "toml==0.10.2",
    "tomli==2.0.1",
    "tqdm==4.64.0",
    "twilio==7.8.1",
    "twine==4.0.0",
    "typing-extensions==4.1.1",
    "tzdata==2022.1",
    "tzlocal==4.2",
    "ua-parser==0.10.0",
    "uritemplate==4.1.1",
    "urllib3==1.26.9",
    "us==2.0.2",
    "user-agents==2.2.0",
    "wcwidth==0.2.5",
    "webencodings==0.5.1",
    "Werkzeug==2.1.1",
    "xfdfgen==0.4",
    "xlrd==2.0.1",
    "XlsxWriter==3.0.3",
    "xlwt==1.3.0",
    "zipp==3.8.0"
]

if sys.version_info < (3, 9):
    install_requires.append("backports.zoneinfo==0.2.1")
else:
    install_requires.append("docassemble-backports==1.0")

setup(name='docassemble.base',
      version='1.4.29',
      python_requires='>=3.8',
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
