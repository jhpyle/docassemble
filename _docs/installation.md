---
layout: docs
title: How to install docassemble
short_title: Installation
---

These installation instructions assume a Debian GNU/Linux machine, but
docassemble has been developed to be operating-system-independent.  If
you can install the dependencies, you should be able to get
docassemble to run.  It has not been tested on Windows (only Debian
and Ubuntu), but all the dependencies are likely to be available for
installation on Windows (see [MiKTeX](http://miktex.org/download) for
LaTeX on Windows).

### Dependencies

The following dependencies can be installed from Debian packages:

    sudo apt-get install python-html2text python-markdown python-yaml \
      python-mako python-dateutil python-setuptools python-httplib2 \
      python-dev python-imaging python-pip wget unzip git locales \
      pandoc texlive texlive-latex-extra

docassemble uses locale settings to format numbers, get currency
symbols, and other things.  Do `echo $LANG` to see what locale you are
using.  If it is not something like `en_US.UTF8`, you will want to set
up an appropriate locale for your region:

    sudo dpkg-reconfigure locales

(On Ubuntu, you may need to do `sudo apt-get install language-pack-en`.)

To install the
[Nodebox English Linguistics library](https://www.nodebox.net/code/index.php/Linguistics),
do:

    wget https://www.nodebox.net/code/data/media/linguistics.zip
    sudo unzip linguistics.zip -d /usr/local/lib/python2.7/dist-packages
    rm linguistics.zip

To install the [us](https://pypi.python.org/pypi/us) and
[SmartyPants](https://pypi.python.org/pypi/mdx_smartypants) modules,
do:

    sudo pip install us 3to2 guess-language-spirit mdx_smartypants titlecase

(The mdx_smartypants module depends on 3to2 and guess-language-spirit,
and may have trouble installing if those modules are not already
installed.)

To install [PyRTF-ng](https://github.com/nekstrom/pyrtf-ng), which is
needed for generating RTF files, do:

    git clone https://github.com/nekstrom/pyrtf-ng
    cd pyrtf-ng
    sudo python setup.py install
	cd ..

The following will install the Debian dependencies needed for the web
server:

    sudo apt-get install apache2 postgresql python-psycopg2 \
      libapache2-mod-wsgi python-bcrypt python-speaklater \
	  poppler-utils python-pil libffi-dev libffi6 libjs-jquery \
	  imagemagick

To install the additional dependencies for the web server
([WTForms](https://wtforms.readthedocs.org/en/latest/),
[rauth](https://github.com/litl/rauth),
[simplekv](https://github.com/mbr/simplekv),
[Flask-KVSession](https://pypi.python.org/pypi/Flask-KVSession),
[Flask-User](https://pythonhosted.org/Flask-User), and
[PyPDF](https://pypi.python.org/pypi/pyPdf/1.13)), do:

    sudo pip install cffi wtforms werkzeug rauth simplekv Flask-KVSession \
      flask-user pypdf flask flask-login flask-sqlalchemy Flask-WTF \
	  babel blinker sqlalchemy

### Installing docassemble

Clone the repository (e.g., in your home directory):

    git clone https://github.com/jhpyle/docassemble

This creates a directory called `docassemble`.  To install the docassemble packages, do the following as root:

    cd ~/docassemble
    sudo ./compile.sh
	cd ..

The compile.sh script installs the four Python packages contained in
the git repository:

1. docassemble
2. docassemble_base
3. docassemble_webapp
4. docassemble_demo

The "docassemble" package is empty because it is a "namespace"
package.  (This facilitates the creation of add-on packages.)  The
core functionality is in the docassemble_base package.  These two
packages are the only packages required to use the docassemble module.
If you do not want to install all the packages, you can skip running
compile.sh and simply run `python setup.py install` in each of the
packages you wish to install.

The `docassemble_webapp` package contains the standard docassemble web
application.  The `docassemble_demo` package contains a demonstration
interview.

## Testing docassemble

The following will run a test of the core docassemble module.  This
requires `docassemble`, `docassemble_base`, and `docassemble_demo` to
be installed.

    cd ~/docassemble
    python docassemble_base/tests/test-parse.py

The output should end with:

    Need to ask:
      Your use of this system does not mean that you have a lawyer.
	  Do you understand this?

## Setting up the web server

The following instructions assume a Debian system on which you have
cloned `docassemble` into your home directory.  You will have to make
some changes to adapt this to your platform.

Enable the Apache wsgi module if it is not already enabled:

    sudo a2enmod wsgi

Create the root directory for user-contributed Python packages (see
[site.USER_BASE](https://pythonhosted.org/setuptools/easy_install.html#custom-installation-locations)),
and make sure it is writeable:

    sudo mkdir -p /var/www/.local
    sudo chown www-data.www-data /var/www/.local

Create the directory for the Flask WSGI file needed by the web server:

    sudo mkdir -p /var/lib/docassemble/webapp
    sudo cp ~/docassemble/docassemble_webapp/flask.wsgi /var/lib/docassemble/webapp
	sudo chown www-data.www-data /var/lib/docassemble/webapp/flask.wsgi

Create the uploads directory:

    sudo mkdir -p /usr/share/docassemble/files
    sudo chown www-data.www-data /usr/share/docassemble/files

Set up and edit the configuration file (e.g., to edit the default
e-mail addresses):

    sudo mkdir -p /etc/docassemble
    sudo cp ~/docassemble/docassemble_base/config.yml /etc/docassemble/
    sudo vi /etc/docassemble/config.yml

Set /etc/apache2/sites-available/000-default.conf to something like:

    <VirtualHost *:80>
      ServerName example.com
      ServerAdmin webmaster@example.com
      Redirect / https://example.com/
      ErrorLog ${APACHE_LOG_DIR}/error.log
      CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>
    <IfModule mod_ssl.c>
      <VirtualHost *:443>
        ServerName example.com
        ServerAdmin webmaster@example.com
        SSLEngine on
        SSLCertificateFile /etc/ssl/example.com.crt
        SSLCertificateKeyFile /etc/ssl/example.com.key 
        SSLCertificateChainFile /etc/ssl/sub.class1.server.ca.pem
        SSLProxyEngine on
        DocumentRoot /var/www/html

        WSGIDaemonProcess docassemble.webserver user=www-data group=www-data threads=5
        WSGIScriptAlias /demo /var/lib/docassemble/webapp/flask.wsgi
        <Directory /var/lib/docassemble/webapp>
          WSGIProcessGroup docassemble.webserver
          WSGIApplicationGroup %{GLOBAL}
          AllowOverride none
          Require all granted
        </Directory>

        ErrorLog /var/log/apache2/error.log
        LogLevel warn
        CustomLog /var/log/apache2/access-da.log combined
      </VirtualHost>
    </IfModule>

You can run `docassemble` on HTTP rather than HTTPS if you want to,
but since the `docassemble` web application uses a password system, it
is a good idea to run it on HTTPS.  If you want to run docassemble on
HTTP, copy the `WSGIDaemonProcess` line, the `WSGIScriptAlias` line,
and the `Directory` section into the `<VirtualHost *:80>` section of
your Apache configuration file.

`docassemble` uses a SQL database.  These instructions assume a
PostgreSQL database, but any database compatible with Python's
sqlalchemy should work with appropriate changes to the
`/etc/docassemble/config.yml` file.  Set up the database by running:

    echo 'create role "www-data" login; create database docassemble;' | sudo -u postgres psql
    sudo -u postgres python ~/docassemble/docassemble_webapp/docassemble/webapp/create_tables.py
    echo 'grant all on all tables in schema public to "www-data"; grant all on all sequences in schema public to "www-data";' | sudo -u postgres psql docassemble

In order for the "Sign in with Google" and "Sign in with Facebook"
buttons to work, you will need to register your site on
[Google Developers Console](https://console.developers.google.com/)
and on [Facebook Developers](https://developers.facebook.com/) and
obtain IDs and secrets, which you supply to docassemble by editing
/etc/docassemble/config.yml.

The /etc/docassemble/config.yml file also contains configuration for
connecting to the Postgresql database and the mail server.

Restart Apache:

    sudo /etc/init.d/apache2 restart

or, if you use systemd:

    sudo systemctl restart apache2.service

The system will be running at http://example.com/demo.

# Upgrading

To upgrade docassemble to the latest version, do:

    cd docassemble
    git pull
    sudo ./compile.sh && sudo touch /var/lib/docassemble/flask.wsgi

Note that after making changes to docassemble interviews and Python
code, it is not necessary to restart Apache.  Changing the
modification time of /var/lib/docassemble/flask.wsgi will trigger
Apache to restart the WSGI processes.

# Debugging the web app

If you get a standard Apache error message, look in
/var/log/apache2/error.log.  If you get an abbreviated message, the
error message is probably in /tmp/flask.log.
