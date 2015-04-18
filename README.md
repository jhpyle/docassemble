# Document assembly module

A python module for assembling documents from templates while
automatically querying a user for necessary information.

## Web site

See the [docassemble web site](http://docassemble.org) to read about the purpose of the software and to run a demo.

## Requirements

The docassemble module depends on:
* mako ([Mako Templates for Python](http://www.makotemplates.org/))
* yaml ([PyYAML](http://pyyaml.org/))
* markdown ([Python-Markdown](https://pythonhosted.org/Markdown))
* [html2text](https://github.com/aaronsw/html2text)
* en ([Nodebox English Linguistics library](https://www.nodebox.net/code/index.php/Linguistics))
* [pandoc](http://johnmacfarlane.net/pandoc/), which depends on [LaTeX](http://www.latex-project.org/) if you want to convert to PDF
* [httplib2](https://pypi.python.org/pypi/httplib2)
* [us](https://pypi.python.org/pypi/us)
* [SmartyPants](https://pypi.python.org/pypi/mdx_smartypants)
* [PyRTF-ng](https://github.com/nekstrom/pyrtf-ng)

The sample web application depends on:
* [Flask](http://flask.pocoo.org/)
* [Bootstrap](http://getbootstrap.com) (hotlinked)
* [Jasny Bootstrap](http://jasny.github.io/bootstrap/) (hotlinked)
* [jQuery](http://jquery.com/) (hotlinked)
* [jQuery Validation](http://jqueryvalidation.org/) (hotlinked)
* [PostgreSQL](http://www.postgresql.org/)
* [psycopg2](http://initd.org/psycopg/)
* [rauth](https://github.com/litl/rauth)
* [simplekv](https://github.com/mbr/simplekv)
* [Flask-KVSession](https://pypi.python.org/pypi/Flask-KVSession)
* [Flask-User](https://pythonhosted.org/Flask-User)
* [Pillow](https://pypi.python.org/pypi/Pillow/)
* [PyPDF](https://pypi.python.org/pypi/pyPdf/1.13)
* [pdftoppm](http://www.foolabs.com/xpdf/download.html)
* A web server
* A mail server

To run the demo question file you will need:
* [DateUtil](https://moin.conectiva.com.br/DateUtil)

## Installation

These installation instructions assume a Debian GNU/Linux machine, but docassemble has been developed to be os-independent.  If you can install the dependencies, you should be able to get docassemble to run.

### Dependencies

The following dependencies can be installed from Debian packages:

    sudo apt-get install python-html2text python-markdown python-yaml \
      python-mako python-dateutil python-setuptools python-httplib2 \
      python-dev python-imaging python-pip wget unzip git locales \
      language-pack-en pandoc texlive

docassemble uses locale settings to format numbers, get currency symbols, and other things.  Do `echo $LANG` to see what locale you are using.  If it is not something like `en_US.UTF8`, you will want to set up an appropriate locale for your region:

    sudo dpkg-reconfigure locales

(On Ubuntu, you may need to do `sudo apt-get install language-pack-en`.)

To install the [Nodebox English Linguistics library](https://www.nodebox.net/code/index.php/Linguistics), do something like the following:

    wget https://www.nodebox.net/code/data/media/linguistics.zip
    sudo unzip linguistics.zip -d /usr/local/lib/python2.7/dist-packages
    rm linguistics.zip

To install the [us](https://pypi.python.org/pypi/us) and [SmartyPants](https://pypi.python.org/pypi/mdx_smartypants) modules, do:

    sudo pip install us 3to2 guess-language-spirit mdx_smartypants

(The mdx_smartypants module depends on 3to2 and guess-language-spirit, and may have trouble installing if those modules are not already installed.)

To install [PyRTF-ng](https://github.com/nekstrom/pyrtf-ng), do:

    git clone https://github.com/nekstrom/pyrtf-ng
    cd pyrtf-ng
    sudo python setup.py install

The following will install the Debian dependencies needed for the web server:

    sudo apt-get install apache2 postgresql python-psycopg2 \
      libapache2-mod-wsgi python-flask python-flask-login \
      python-flask-sqlalchemy python-flaskext.wtf python-passlib \
      python-flask-babel python-bcrypt python-speaklater poppler-utils \
      python-pil

To install the additional dependencies for the web server ([rauth](https://github.com/litl/rauth), [simplekv](https://github.com/mbr/simplekv), [Flask-KVSession](https://pypi.python.org/pypi/Flask-KVSession), [Flask-User](https://pythonhosted.org/Flask-User)), and [PyPDF](https://pypi.python.org/pypi/pyPdf/1.13), do:

    sudo pip install rauth simplekv Flask-KVSession flask-user pypdf

### Installing docassemble

Clone the repository (e.g., in your home directory):

    git clone https://github.com/jhpyle/docassemble

This creates a directory called `docassemble`.  To install the docassemble packages, do the following as root:

    cd docassemble
    sudo ./compile.sh

The compile.sh script installs the four Python packages contained in the git repository:

1. docassemble
2. docassemble-base
3. docassemble-webapp
4. docassemble-demo

The "docassemble" package is empty because it is a "namespace" package.  (This facilitates the creation of add-on packages.)  The core functionality is in the docassemble-base package.  These two packages are the only packages required to use the docassemble module.  If you do not want to install all the packages, you can skip running compile.sh and simply run `python setup.py install` in each of the packages you wish to install.

The "docassemble-webapp" package contains the standard docassemble web application.  The "docassemble-demo" package contains a demonstration interview.

## Testing docassemble

The following will run a test of the core docassemble module.  This requires `docassemble`, `docassemble-base`, and `docassemble-demo` to be installed.

    cd ~/docassemble
    python docassemble-base/tests/test-parse.py

If it fails with an exception, there was a problem with the installation.  The output should end with:

    Need to ask:
      What is your name?

    to get x.name.first

## Setting up the web server

The following instructions assume a Debian system where your username is jdoe and you have cloned docassemble from /home/jdoe.  You will have to make some changes to adapt this to your platform.

Turn on wsgi:

    sudo a2enmod wsgi

Create the python-eggs directory (necessary for using pandoc templates):

    sudo mkdir /var/www/.python-eggs
    sudo chown www-data.www-data /var/www/.python-eggs

Create the directory to hold the Flask WSGI file for the web server:

    sudo mkdir -p /var/lib/docassemble
    sudo mv docassemble/docassemble-webapp/flask.wsgi /var/lib/docassemble/

Create the uploads directory:

    sudo mkdir -p /usr/share/docassemble/files
    sudo chown www-data.www-data /usr/share/docassemble/files

Set up and edit the configuration file:

    sudo mkdir /etc/docassemble
    sudo mv docassemble/docassemble-base/config.yaml /etc/docassemble/
    sudo vi /etc/docassemble/config.yaml

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
        WSGIScriptAlias /demo /var/lib/docassemble/flask.wsgi
        <Directory /var/lib/docassemble>
          WSGIProcessGroup docassemble.webserver
          WSGIApplicationGroup %{GLOBAL}
          AllowOverride none
          Require all granted
        </Directory>
        Alias /robots.txt /var/www/html/robots.txt
        Alias /favicon.ico /var/www/html/favicon.ico
        ErrorLog /var/log/apache2/error.log
        LogLevel warn
        CustomLog /var/log/apache2/access-da.log combined
      </VirtualHost>
    </IfModule>

You can run `docassemble` on HTTP rather than HTTPS if you want to, but since the `docassemble` web application uses a password system, it is a good idea to run it on HTTPS.

Set up the database.  First, do:

    sudo su postgres
    cd ~
    psql

Then, within psql, run the following SQL statements to create the necessary data tables and to give read and write access to the web application:

    create role "www-data" login;
    create database docassemble;
    \c docassemble
    drop table if exists "uploads";
    drop table if exists "kvstore";
    drop table if exists "userdict";
    drop table if exists "attachments";
    drop table if exists "user_auth";
    drop table if exists "user_roles";
    drop table if exists "role";
    drop table if exists "user";
    create table "user" (id serial primary key, social_id varchar(64) not null unique, nickname varchar(64) not null, email varchar(255) unique, confirmed_at timestamp, active boolean not null default 'f', first_name varchar(50) not null default '', last_name varchar(50) not null default '', country varchar(2), subdivisionfirst varchar(2), subdivisionsecond varchar(50), subdivisionthird varchar(50), organization varchar(64));
    grant all on "user" to "www-data";
    grant all on "user_id_seq" to "www-data";
    create table "user_auth" (id serial primary key, user_id integer references "user" (id), password varchar(255) not null default '', reset_password_token varchar(100) not null default '', active boolean not null default 'f');
    grant all on "user_auth" to "www-data";
    grant all on "user_auth_id_seq" to "www-data";
    create table "role" (id serial primary key, name varchar(50) unique, description varchar(255));
    grant all on "role" to "www-data";
    grant all on "role_id_seq" to "www-data";
    insert into "role" (name) values ('admin');
    insert into "role" (name) values ('user');
    insert into "role" (name) values ('developer');
    create table "user_roles" (id serial primary key, user_id integer references "user" (id), role_id integer references "role" (id));
    grant all on "user_roles" to "www-data";
    grant all on "user_roles_id_seq" to "www-data";
    create table "kvstore" (key varchar(250) not null primary key, value bytea not null);
    grant all on "kvstore" to "www-data";
    create table "userdict" (indexno serial, filename text, key varchar(250), dictionary text, user_id integer references "user" (id));
    grant all on "userdict" to "www-data";
    grant all on "userdict_indexno_seq" to "www-data";
    create table "attachments" (key varchar(250), dictionary text, question integer, filename text);
    grant all on "attachments" to "www-data";
    create table "uploads" (indexno serial, key varchar(250), filename text);
    grant all on "uploads" to "www-data";
    grant all on "uploads_indexno_seq" to "www-data";
    \q

In order for the "Sign in with Google" and "Sign in with Facebook" buttons to work, you will need to register your site on [Google Developers Console](https://console.developers.google.com/) and on [Facebook Developers](https://developers.facebook.com/) and obtain IDs and secrets, which you supply to docassemble by editing /etc/docassemble/config.yaml.

The /etc/docassemble/config.yaml file also contains configuration for connecting to the Postgresql database and the mail server.

Restart Apache:

    sudo /etc/init.d/apache2 restart

or

    sudo systemctl restart apache2.service

The system will be running at http://example.com/demo.

## Author

Jonathan Pyle, jhpyle@gmail.com
