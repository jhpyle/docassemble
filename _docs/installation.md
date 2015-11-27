---
layout: docs
title: How to install docassemble
short_title: Installation
---

These installation instructions assume a Debian GNU/Linux machine, but
**docassemble** has been developed to be operating-system-independent.
If you can install the dependencies, you should be able to get
**docassemble** to run.  It has not been tested on Windows (only
Debian and Ubuntu), but all the dependencies are likely to be
available for installation on Windows (see [MiKTeX] for LaTeX on
Windows).

Since **docassemble** has a lot of [dependencies], you may wish to
[run it using Docker] rather than follow all of these installation
instructions.

# Installing dependencies

The following dependencies can be installed from Debian packages:

{% highlight bash %}
sudo apt-get install python-markdown python-yaml python-mako \
  python-dateutil python-setuptools python-httplib2 \
  python-dev python-imaging pandoc texlive texlive-latex-extra \
  gcc wget unzip git locales
{% endhighlight %}
  
docassemble uses locale settings to format numbers, get currency
symbols, and other things.  Do `echo $LANG` to see what locale you are
using.  If it is not something like `en_US.UTF-8`, you will want to set
up an appropriate locale for your region:

{% highlight bash %}
sudo dpkg-reconfigure locales
{% endhighlight %}

(On Ubuntu, you may need to do `sudo apt-get install language-pack-en`.)

To install the [Nodebox English Linguistics library], do:

{% highlight bash %}
wget https://www.nodebox.net/code/data/media/linguistics.zip
sudo unzip linguistics.zip -d /usr/local/lib/python2.7/dist-packages
rm linguistics.zip
{% endhighlight %}

Many of the Python packages used by **docassemble** need to be
downloading using pip, either because they are not available through
`apt-get`, or because the versions available through `apt-get` are too
old.

First, you need to install the latest version of `pip`:

{% highlight bash %}
easy_install pip
{% endhighlight %}

To install the [us](https://pypi.python.org/pypi/us) and
[SmartyPants](https://pypi.python.org/pypi/mdx_smartypants) modules,
do:

{% highlight bash %}
sudo pip install --upgrade us 3to2 guess-language-spirit html2text
sudo pip install --upgrade mdx_smartypants titlecase
sudo pip install --upgrade cffi
sudo pip install --upgrade bcrypt
sudo pip install --upgrade wtforms werkzeug rauth simplekv \
  Flask-KVSession flask-user pypdf flask flask-login \
  flask-sqlalchemy Flask-WTF babel blinker sqlalchemy
{% endhighlight %}

The mdx_smartypants module depends on 3to2 and guess-language-spirit,
and may have trouble installing if those modules are not already
installed.  The cffi and bcrypt packages can give errors if they are
not installed in the right order.

To install [PyRTF-ng](https://github.com/nekstrom/pyrtf-ng), which is
needed for generating RTF files, do:

{% highlight bash %}
git clone https://github.com/nekstrom/pyrtf-ng
cd pyrtf-ng
sudo python setup.py install
cd ..
{% endhighlight %}

The following will install the Debian dependencies needed for the web
server:

{% highlight bash %}
sudo apt-get install apache2 postgresql python-psycopg2 \
  libapache2-mod-wsgi libapache2-mod-xsendfile python-speaklater \
  poppler-utils python-pil libffi-dev libffi6 imagemagick
{% endhighlight %}

To install the additional Python dependencies for the web server
([WTForms](https://wtforms.readthedocs.org/en/latest/),
[rauth](https://github.com/litl/rauth),
[simplekv](https://github.com/mbr/simplekv),
[Flask-KVSession](https://pypi.python.org/pypi/Flask-KVSession),
[Flask-User](https://pythonhosted.org/Flask-User), and
[PyPDF](https://pypi.python.org/pypi/pyPdf/1.13)), do:

{% highlight bash %}
sudo pip install --upgrade wtforms werkzeug rauth simplekv \
  Flask-KVSession flask-user pypdf flask flask-login \
  flask-sqlalchemy Flask-WTF babel blinker sqlalchemy
  Pygments
{% endhighlight %}

If you want to be able to convert uploaded sound files into different
formats, you will also need to install [ffmpeg] and the
[Perl Audio Converter]:

{% highlight bash %}
sudo apt-get install libaudio-flac-header-perl \
  libaudio-musepack-perl libmp3-tag-perl \
  libogg-vorbis-header-pureperl-perl perl make libvorbis-dev \
  libcddb-perl libinline-perl libcddb-get-perl libmp3-tag-perl \
  libaudio-scan-perl libaudio-flac-header-perl \
  libparallel-forkmanager-perl ffmpeg
git clone git://git.code.sf.net/p/pacpl/code pacpl-code 
cd pacpl-code
./configure
make
sudo make install
cd ..
{% endhighlight %}

# Installing docassemble

Clone the repository (e.g., in your home directory):

{% highlight bash %}
git clone https://github.com/jhpyle/docassemble
{% endhighlight %}

This creates a directory called `docassemble`.  To install the
docassemble packages, do the following as root:

{% highlight bash %}
cd ~/docassemble
sudo ./compile.sh
cd ..
{% endhighlight %}

The compile.sh script installs the four Python packages contained in
the git repository:

1. docassemble: empty namespace package;
2. docassemble.base: core functionality;
3. docassemble.mako: version of [Mako] modified slightly to work with **docassemble**;
4. docassemble.webapp: the web application framework
5. docassemble.demo: demonstration interview package

The "docassemble" package is empty because it is a "namespace"
package.  (This facilitates the creation of add-on packages.)  The
core functionality is in the `docassemble.base` package.  These two
packages are the only packages required to use the docassemble module.
If you do not want to install all the packages, you can skip running
compile.sh and simply run `python setup.py install` in each of the
packages you wish to install.

The `docassemble.webapp` package contains the standard docassemble web
application.  The `docassemble.demo` package contains a demonstration
interview.

# Testing docassemble

The following will run a test of the core docassemble module.  This
requires `docassemble`, `docassemble.base`, `docassemble.mako`, and
`docassemble.demo` to be installed.

{% highlight bash %}
cd ~/docassemble
python docassemble_base/tests/test-parse.py
{% endhighlight %}

The output should end with:

{% highlight bash %}
Need to ask:
  Your use of this system does not mean that you have a lawyer.
  Do you understand this?
{% endhighlight %}

# Setting up the web server

The following instructions assume a Debian/Ubuntu system on which you have
cloned `docassemble` into your home directory.  You will have to make
some changes to adapt this to your platform.

Enable the Apache wsgi and xsendfile modules if they are not already enabled:

{% highlight bash %}
sudo a2enmod wsgi
sudo a2enmod xsendfile
{% endhighlight %}

Create the root directory for user-contributed Python packages (see
[site.USER_BASE]), and make sure it is writeable:

{% highlight bash %}
sudo mkdir -p /var/www/.local /var/www/.cache
sudo chown www-data.www-data /var/www/.local /var/www/.cache
{% endhighlight %}

Create the directory for the Flask WSGI file needed by the web server:

{% highlight bash %}
sudo mkdir -p /var/lib/docassemble/webapp
sudo cp ~/docassemble/docassemble_webapp/flask.wsgi /var/lib/docassemble/webapp
sudo chown www-data.www-data /var/lib/docassemble/webapp/flask.wsgi
{% endhighlight %}

Create the uploads directory:

{% highlight bash %}
sudo mkdir -p /usr/share/docassemble/files
sudo chown www-data.www-data /usr/share/docassemble/files
{% endhighlight %}

Set up and edit the [configuration] file.  At the very least, you should
edit the `secretkey` value to something random and unique to your
site.

{% highlight bash %}
sudo mkdir -p /etc/docassemble
sudo cp ~/docassemble/docassemble_base/config.yml /etc/docassemble/
sudo vi /etc/docassemble/config.yml
{% endhighlight %}

Set /etc/apache2/sites-available/000-default.conf to something like:

{% highlight text %}
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
    XSendFile on
    XSendFilePath /usr
    XSendFilePath /var
    XSendFilePath /tmp
    WSGIDaemonProcess docassemble.webserver user=www-data group=www-data threads=5
    WSGIScriptAlias /da /var/lib/docassemble/webapp/docassemble.wsgi
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
{% endhighlight %}

You can run `docassemble` on HTTP rather than HTTPS if you want to,
but since the `docassemble` web application uses a password system, it
is a good idea to run it on HTTPS.  If you want to run docassemble on
HTTP, copy the `WSGIDaemonProcess` line, the `WSGIScriptAlias` line,
and the `Directory` section into the `<VirtualHost *:80>` section of
your Apache configuration file.

If your **docassemble** interviews are not thread-safe, for example
because different interviews use different locales, change `threads=5`
to `processes=5 threads=1`.  This will cause Apache to run WSGI in a
"prefork" configuration.  This is slower than the multi-thread
configuration.

`docassemble` uses a SQL database.  Set up the database by running the
following commands.  (You may wish to make changes to the database
information in `/etc/docassemble/config.yml` first.)

{% highlight bash %}
echo 'create role "www-data" login; create database docassemble;' | sudo -u postgres psql
sudo -u postgres python ~/docassemble/docassemble_webapp/docassemble/webapp/create_tables.py /etc/docassemble/config.yml
echo 'grant all on all tables in schema public to "www-data"; grant all on all sequences in schema public to "www-data";' | sudo -u postgres psql docassemble
{% endhighlight %}

In order for the "Sign in with Google" and "Sign in with Facebook"
buttons to work, you will need to register your site on
[Google Developers Console](https://console.developers.google.com/)
and on [Facebook Developers](https://developers.facebook.com/) and
obtain IDs and secrets, which you supply to docassemble by editing
the `/etc/docassemble/config.yml` [configuration] file.

The `/etc/docassemble/config.yml` file also contains settings for
connecting to the PostgreSQL database and the mail server.

Restart Apache:

{% highlight bash %}
sudo /etc/init.d/apache2 restart
{% endhighlight %}

or, if you use systemd:

{% highlight bash %}
sudo systemctl restart apache2.service
{% endhighlight %}

The system will be running at http://example.com/da.

## Using different web servers and/or SQL database backends

**docassemble** is not dependent on Apache or PostgreSQL.  Other web
servers that can host Python WSGI applications (e.g., nginx with
uWSGI) could be used.

**docassemble** uses [SQLAlchemy] to communicate with the SQL back
end, so you could edit the [configuration] to point to another type of
database system, if supported by [SQLAlchemy].  **docassemble** does
not do fancy things with SQL, so most backends should work without a
problem.  Any backend used must support column definitions with
`server_default=db.func.now()`.

# Upgrading docassemble

To upgrade docassemble to the latest version, do:

{% highlight bash %}
cd docassemble
git pull
sudo ./compile.sh && sudo touch /var/lib/docassemble/docassemble.wsgi
{% endhighlight %}

Note that after making changes to docassemble interviews and Python
code, it is not necessary to restart Apache.  Changing the
modification time of /var/lib/docassemble/docassemble.wsgi will trigger
Apache to restart the WSGI processes.

# Debugging the web app

If you get a standard Apache error message, look in
/var/log/apache2/error.log.  If you get an abbreviated message, the
error message is probably in /tmp/flask.log.

[dependencies]: {{ site.baseurl }}/docs/requirements.html
[run it using Docker]: {{ site.baseurl }}/docs/docker.html
[MiKTeX]: http://miktex.org/download
[Nodebox English Linguistics library]: https://www.nodebox.net/code/index.php/Linguistics
[site.USER_BASE]: https://pythonhosted.org/setuptools/easy_install.html#custom-installation-locations
[configuration]: {{ site.baseurl }}/docs/config.html
[Perl Audio Converter]: http://vorzox.wix.com/pacpl
[ffmpeg]: https://www.ffmpeg.org/
[SQLAlchemy]: http://www.sqlalchemy.org/
[Mako]: http://www.makotemplates.org/
