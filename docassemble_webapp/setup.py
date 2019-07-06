import os
from setuptools import setup, find_packages
from six import PY2

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

if PY2:
    install_requires = ['docassemble==0.4.59', 'docassemble.base==0.4.59', 'docassemble.demo==0.4.59', 'beautifulsoup4', 'boto', 'boto3', 'celery[redis]==4.1.0', 'kombu==4.1.0', 'eventlet', 'greenlet', 'flask', 'flask-kvsession', 'flask-login', 'flask-mail', 'flask-sqlalchemy', 'flask-user<0.7', 'flask-babel', 'flask-wtf', 'flask-socketio', 'flask-cors', 'pip', 'psycopg2-binary', 'python-dateutil', 'rauth', 'requests', 'wtforms==2.1', 'setuptools', 'sqlalchemy', 'tailer', 'werkzeug', 'simplekv', 'gcs-oauth2-boto-plugin', 'psutil', 'twilio', 'pycurl', 'google-api-python-client', 'azure-storage', 'rfc3339', 'iso8601', 'pyotp', 'links-from-link-header', 'alembic', 'sklearn', 'scipy', 'gspread', 'oauth2client', 'google-auth', 'google-cloud-translate', 'google-cloud-storage', 'iso8601', 'textstat==0.5.4', 'XlsxWriter', 'netifaces']
else:
    install_requires = ['docassemble==0.4.59', 'docassemble.base==0.4.59', 'docassemble.demo==0.4.59', 'beautifulsoup4', 'boto', 'boto3', 'celery[redis]', 'kombu', 'eventlet', 'greenlet', 'flask', 'flask-kvsession', 'flask-login', 'flask-mail', 'flask-sqlalchemy', 'flask-user<0.7', 'flask-babel', 'flask-wtf', 'flask-socketio', 'flask-cors', 'pip', 'psycopg2-binary', 'python-dateutil', 'rauth', 'requests', 'wtforms==2.1', 'setuptools', 'sqlalchemy', 'tailer', 'werkzeug', 'simplekv', 'gcs-oauth2-boto-plugin', 'psutil', 'twilio', 'pycurl', 'google-api-python-client', 'azure-storage', 'rfc3339', 'iso8601', 'pyotp', 'links-from-link-header', 'alembic', 'sklearn', 'scipy', 'gspread', 'oauth2client', 'google-auth', 'google-cloud-translate', 'google-cloud-storage', 'iso8601', 'textstat==0.5.4', 'XlsxWriter', 'netifaces']

setup(name='docassemble.webapp',
      version='0.4.59',
      description=('The web application components of the docassemble system.'),
      long_description=read("README.md"),
      long_description_content_type='text/markdown',
      author='Jonathan Pyle',
      author_email='jhpyle@gmail.com',
      license='MIT',
      url='https://docassemble.org',
      download_url='https://download.docassemble.org/docassemble-webapp.tar.gz',
      packages=find_packages(),
      namespace_packages = ['docassemble'],
      install_requires = install_requires,
      zip_safe = False,
      package_data={'docassemble.webapp': ['alembic.ini', os.path.join('alembic', '*'), os.path.join('alembic', 'versions', '*'), os.path.join('data', '*.*'), os.path.join('data', 'static', '*.*'), os.path.join('data', 'static', 'favicon', '*.*'), os.path.join('data', 'questions', '*.*'), os.path.join('templates', 'base_templates', '*.html'), os.path.join('templates', 'flask_user', '*.html'), os.path.join('templates', 'flask_user', 'emails', '*.*'), os.path.join('templates', 'pages', '*.html'), os.path.join('templates', 'pages', '*.xml'), os.path.join('templates', 'users', '*.html'), os.path.join('static', 'app', '*.*'), os.path.join('static', 'sounds', '*.*'), os.path.join('static', 'examples', '*.*'), os.path.join('static', 'fontawesome', 'js', '*.*'), os.path.join('static', 'fontawesome', 'css', '*.*'), os.path.join('static', 'office', '*.*'), os.path.join('static', 'bootstrap-fileinput', 'img', '*'), os.path.join('static', 'bootstrap-fileinput', 'themes', 'fas', '*'), os.path.join('static', 'bootstrap-fileinput', 'js', 'locales', '*'), os.path.join('static', 'bootstrap-fileinput', 'js', 'plugins', '*'), os.path.join('static', 'bootstrap-slider', 'dist', '*.js'), os.path.join('static', 'bootstrap-slider', 'dist', 'css', '*.css'), os.path.join('static', 'bootstrap-fileinput', 'css', '*.css'), os.path.join('static', 'bootstrap-fileinput', 'js', '*.js'), os.path.join('static', 'bootstrap-fileinput', 'themes', 'fa', '*.js'), os.path.join('static', 'bootstrap-fileinput', 'themes', 'fas', '*.js'), os.path.join('static', 'bootstrap-combobox', 'css', '*.css'), os.path.join('static', 'bootstrap-combobox', 'js', '*.js'), os.path.join('static', 'bootstrap-fileinput', '*.md'), os.path.join('static', 'bootstrap', 'js', '*.*'), os.path.join('static', 'bootstrap', 'css', '*.*'), os.path.join('static', 'labelauty', 'source', '*.*'), os.path.join('static', 'codemirror', 'lib', '*.*'), os.path.join('static', 'codemirror', 'addon', 'search', '*.*'), os.path.join('static', 'codemirror', 'addon', 'display', '*.*'), os.path.join('static', 'codemirror', 'addon', 'scroll', '*.*'), os.path.join('static', 'codemirror', 'addon', 'dialog', '*.*'), os.path.join('static', 'codemirror', 'addon', 'edit', '*.*'), os.path.join('static', 'codemirror', 'addon', 'hint', '*.*'), os.path.join('static', 'codemirror', 'mode', 'yaml', '*.*'), os.path.join('static', 'codemirror', 'mode', 'markdown', '*.*'), os.path.join('static', 'codemirror', 'mode', 'javascript', '*.*'), os.path.join('static', 'codemirror', 'mode', 'css', '*.*'), os.path.join('static', 'codemirror', 'mode', 'python', '*.*'), os.path.join('static', 'codemirror', 'mode', 'htmlmixed', '*.*'), os.path.join('static', 'codemirror', 'mode', 'xml', '*.*'), os.path.join('static', 'codemirror', 'keymap', '*.*'), os.path.join('static', 'areyousure', '*.js'), os.path.join('static', 'popper', '*.*'), os.path.join('static', 'popper', 'umd', '*.*'), os.path.join('static', 'popper', 'esm', '*.*')]},
     )
