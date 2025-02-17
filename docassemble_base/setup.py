import os
from fnmatch import fnmatchcase
from setuptools import setup, find_namespace_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', os.path.join('.', 'build'), os.path.join('.', 'dist'), 'EGG-INFO', '*.egg-info')


def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(os.path.normpath(where), '', package)]
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
    "3to2==1.1.1",
    "aiohappyeyeballs==2.4.3",
    "aiohttp==3.11.8",
    "aiohttp-retry==2.8.3",
    "aiosignal==1.3.1",
    "alembic==1.14.0",
    "anyio==4.6.2.post1",
    "astunparse==1.6.3",
    "async-timeout==5.0.1",
    "atomicwrites==1.4.1",
    "attrs==24.2.0",
    "azure-common==1.1.28",
    "azure-core==1.32.0",
    "azure-identity==1.19.0",
    "azure-keyvault-secrets==4.9.0",
    "azure-nspkg==3.0.2",
    "azure-storage-blob==12.24.0",
    "babel==2.16.0",
    "backports.tarfile==1.2.0",
    "bcrypt==4.2.1",
    "beautifulsoup4==4.12.3",
    "bleach==6.2.0",
    "blinker==1.9.0",
    "boto==2.49.0",
    "boto3==1.35.71",
    "botocore==1.35.71",
    "cachetools==5.5.0",
    "cairocffi==1.7.1",
    "CairoSVG==2.7.1",
    "certifi==2024.8.30",
    "cffi==1.17.1",
    "chardet==5.2.0",
    "charset-normalizer==3.4.0",
    "click==8.1.7",
    "colorama==0.4.6",
    "commonmark==0.9.1",
    "convertapi==2.0.0",
    "cryptography==44.0.0",
    "cssselect2==0.7.0",
    "defusedxml==0.7.1",
    "Deprecated==1.2.15",
    "deprecation==2.1.0",
    "docassemble-backports==1.0",
    "Docassemble-Pattern==3.6.7",
    "docassemble-textstat==0.7.2",
    "docopt==0.6.2",
    "docutils==0.21.2",
    "docxcompose==1.4.0",
    "docxtpl==0.19.0",
    "et_xmlfile==2.0.0",
    "exceptiongroup==1.2.2",
    "Flask==3.1.0",
    "Flask-Mail==0.10.0",
    "frozenlist==1.5.0",
    "future==1.0.0",
    "geographiclib==2.0",
    "geopy==2.4.1",
    "google-api-core==2.23.0",
    "google-api-python-client==2.154.0",
    "google-auth==2.17.0",
    "google-auth-httplib2==0.2.0",
    "google-auth-oauthlib==1.2.1",
    "google-cloud-core==2.4.1",
    "google-cloud-storage==2.11.0",
    "google-cloud-vision==3.8.1",
    "google-crc32c==1.6.0",
    "google-i18n-address==3.1.1",
    "google-resumable-media==2.7.2",
    "googleapis-common-protos==1.66.0",
    "greenlet==3.1.1",
    "grpcio==1.68.0",
    "grpcio-status==1.68.0",
    "guess-language-spirit==0.5.3",
    "httplib2==0.22.0",
    "Hyphenate==1.1.0",
    "idna==3.10",
    "img2pdf==0.5.1",
    "importlib_metadata==8.5.0",
    "importlib_resources==6.4.5",
    "iniconfig==2.0.0",
    "isodate==0.7.2",
    "itsdangerous==2.2.0",
    "jaraco.classes==3.4.0",
    "jaraco.context==6.0.1",
    "jaraco.functools==4.1.0",
    "jdcal==1.4.1",
    "jeepney==0.8.0",
    "jellyfish==1.1.0",
    "Jinja2==3.1.4",
    "jmespath==1.0.1",
    "joblib==1.4.2",
    "keyring==25.5.0",
    "lxml==5.3.0",
    "Mako==1.3.6",
    "Markdown==3.7",
    "markdown-it-py==3.0.0",
    "MarkupSafe==3.0.2",
    "mdurl==0.1.2",
    "more-itertools==10.5.0",
    "msal==1.31.1",
    "msal-extensions==1.2.0",
    "msrest==0.7.1",
    "multidict==6.1.0",
    "namedentities==1.9.4",
    "nh3==0.2.19",
    "nltk==3.9.1",
    "num2words==0.5.13",
    "numpy==2.1.3",
    "oauth2client==4.1.3",
    "oauthlib==3.2.2",
    "openpyxl==3.1.5",
    "ordered-set==4.1.0",
    "packaging==24.2",
    "pandas==2.2.3",
    "passlib==1.7.4",
    "pdfminer.six==20240706",
    "phonenumbers==8.13.50",
    "pikepdf==9.4.2",
    "pillow==11.0.0",
    "pkginfo==1.11.2",
    "pluggy==1.5.0",
    "ply==3.11",
    "portalocker==2.10.1",
    "propcache==0.2.0",
    "proto-plus==1.25.0",
    "protobuf==5.29.0",
    "pyasn1==0.6.1",
    "pyasn1_modules==0.4.1",
    "pycountry==24.6.1",
    "pycparser==2.22",
    "pycryptodome==3.21.0",
    "pycryptodomex==3.21.0",
    "Pygments==2.18.0",
    "PyJWT==2.10.1",
    "PyLaTeX==1.4.2",
    "pyparsing==3.2.0",
    "pypng==0.20220715.0",
    "pytest==8.3.3",
    "python-dateutil==2.9.0.post0",
    "python-docx==1.1.2",
    "python-editor==1.0.4",
    "pytz==2024.2",
    "pytz-deprecation-shim==0.1.0.post0",
    "PyYAML==6.0.2",
    "pyzbar==0.1.9",
    "qrcode==8.0",
    "readme_renderer==44.0",
    "regex==2024.11.6",
    "reportlab==4.2.5",
    "repoze.lru==0.7",
    "requests==2.32.3",
    "requests-oauthlib==2.0.0",
    "requests-toolbelt==1.0.0",
    "rfc3986==2.0.0",
    "rich==13.9.4",
    "rsa==4.7.2",
    "ruamel.yaml==0.18.6",
    "ruamel.yaml.bytes==0.1.0",
    "ruamel.yaml.clib==0.2.12",
    "ruamel.yaml.string==0.1.1",
    "s3transfer==0.10.4",
    "scipy==1.14.1",
    "SecretStorage==3.3.3",
    "six==1.16.0",
    "sniffio==1.3.1",
    "sortedcontainers==2.4.0",
    "soupsieve==2.6",
    "SQLAlchemy==2.0.36",
    "tinycss2==1.4.0",
    "titlecase==2.4.1",
    "toml==0.10.2",
    "tomli==2.2.1",
    "tqdm==4.67.1",
    "twilio==9.3.7",
    "twine==6.0.0",
    "typing_extensions==4.12.2",
    "tzdata==2024.2",
    "tzlocal==5.2",
    "ua-parser==1.0.0",
    "ua-parser-builtins==0.18.0",
    "uritemplate==4.1.1",
    "urllib3==2.2.3",
    "us==3.2.0",
    "user-agents==2.2.0",
    "wcwidth==0.2.13",
    "webencodings==0.5.1",
    "Werkzeug==3.1.3",
    "wrapt==1.17.0",
    "xfdfgen==0.4",
    "xlrd==2.0.1",
    "XlsxWriter==3.2.0",
    "xlwt==1.3.0",
    "yarl==1.18.0",
    "zipp==3.21.0"
]

setup(name='docassemble.base',
      version='1.6.3',
      python_requires='>=3.9',
      description=('The base components of the docassemble system.'),
      long_description=read("README.md"),
      long_description_content_type='text/markdown',
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='https://docassemble.org',
      install_requires=install_requires,
      packages=find_namespace_packages(include=['docassemble.*']),
      zip_safe=False,
      package_data=find_package_data(where=os.path.join('docassemble', 'base', ''), package='docassemble.base'),
      )
