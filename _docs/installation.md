---
layout: docs
title: How to install docassemble
short_title: Installation
---

These installation instructions assume you are installing into a
Debian/Ubuntu environment, but **docassemble** has been developed to
be operating-system-independent.  If you can install the dependencies,
you should be able to get **docassemble** to run.  It has not been
tested on Windows, but all the dependencies are likely to be available
for installation on Windows (see [MiKTeX] for LaTeX on Windows).

Since **docassemble** has a lot of [dependencies], you may wish to
[run it using Docker] rather than follow all of these installation
instructions.

For instructions on installing **docassemble** in a multi-server
arrangement, for example on [Amazon EC2], see the [scalability]
section.

# Installing dependencies

## Underlying packages

The following dependencies can be installed from [Debian] packages:

{% highlight bash %}
sudo apt-get install python python-dev pandoc texlive texlive-latex-extra \
  gcc wget unzip git locales libjpeg-dev libpq-dev apache2 postgresql \
  libapache2-mod-wsgi libapache2-mod-xsendfile poppler-utils \
  libffi-dev libffi6 imagemagick libav-tools logrotate tmpreaper cron \
  libaudio-flac-header-perl libaudio-musepack-perl libmp3-tag-perl \
  libogg-vorbis-header-pureperl-perl perl make libvorbis-dev \
  libcddb-perl libinline-perl libcddb-get-perl libmp3-tag-perl \
  libaudio-scan-perl libaudio-flac-header-perl \
  libparallel-forkmanager-perl
{% endhighlight %}

**docassemble** depends on the [Perl Audio Converter] to convert
uploaded sound files into other formats.  The version in [Debian] is
not recent enough, so you will have to install it by hand:

{% highlight bash %}
sudo apt-get install 
git clone git://git.code.sf.net/p/pacpl/code pacpl-code 
cd pacpl-code
./configure
make
sudo make install
cd ..
{% endhighlight %}

docassemble uses locale settings to format numbers, get currency
symbols, and other things.  Do `echo $LANG` to see what locale you are
using.  If it is not something like `en_US.UTF-8`, you will want to set
up an appropriate locale for your region:

{% highlight bash %}
sudo dpkg-reconfigure locales
{% endhighlight %}

(On Ubuntu, you may need to do `sudo apt-get install language-pack-en`.)

## Python and its packages

The recommended way to install **docassemble**'s [Python] dependencies
is to create a [Python virtual environment] that belongs to the web
server user (`www-data` on Debian/Ubuntu), and to install the packages
using [pip].

There are two reasons for this.  First, this will allow developers to
install new Python packages through the web interface, without having
to use the command line.  Second, this will ensure that all of the
Python packages are the latest version; the versions that are packaged
with Linux distributions are not always current.

Before setting up the [Python virtual environment] as `www-data`, we
need to create a directory needed by [pip] for temporary files, and a
directory in which to install [Python] and its modules:

{% highlight bash %}
mkdir -p /var/www/.pip /usr/share/docassemble/local
chown www-data.www-data /var/www/.pip /usr/share/docassemble
{% endhighlight %}

You may also need to run the following in order to run commands as
`www-data`:

{% highlight bash %}
chsh -s /bin/bash www-data
{% endhighlight %}

Then run the following as `www-data`:

{% highlight bash %}
virtualenv /usr/share/docassemble/local
source /usr/share/docassemble/local/bin/activate
pip install --upgrade us 3to2 guess-language-spirit html2text markdown \
  pyyaml mako python-dateutil setuptools httplib2 psycopg2 pillow \
  mdx_smartypants titlecase pygeocoder beautifulsoup4 cffi tailer bcrypt \
  speaklater wtforms werkzeug rauth simplekv Flask-KVSession flask-user \
  pypdf flask flask-login flask-sqlalchemy Flask-WTF babel blinker \
  sqlalchemy Pygments boto
{% endhighlight %}

Finally, there are some [Python] packages that need to be installed
manually.

To install the [Nodebox English Linguistics library], do the following
as `www-data`:

{% highlight bash %}
cd /tmp
wget https://www.nodebox.net/code/data/media/linguistics.zip
unzip linguistics.zip -d /usr/share/docassemble/local/lib/python2.7/site-packages/
rm linguistics.zip
{% endhighlight %}

To install [PyRTF-ng](https://github.com/nekstrom/pyrtf-ng), which is
needed for generating RTF files, run the following as `www-data`:

{% highlight bash %}
cd /tmp
git clone https://github.com/nekstrom/pyrtf-ng
cd pyrtf-ng
python setup.py install
cd ..
{% endhighlight %}

# Installing docassemble

The **docassemble** application itself is on [GitHub].  Clone the
repository (e.g., in your home directory):

{% highlight bash %}
git clone https://github.com/jhpyle/docassemble
{% endhighlight %}

This creates a directory called `docassemble` in the current
directory.  To install the docassemble packages, do the following as
`www-data`:

{% highlight bash %}
cd docassemble
sudo ./compile.sh
cd ..
{% endhighlight %}

The compile.sh script installs the five Python packages contained in
the git repository:

1. docassemble: empty namespace package;
2. docassemble.base: core functionality;
3. docassemble.mako: version of [Mako] modified slightly to work with **docassemble**;
4. docassemble.webapp: the web application framework
5. docassemble.demo: demonstration interview package

The script installs these packages into the virtual environment
located at `/usr/share/docassemble/local`.

The "docassemble" package is empty because it is a "namespace"
package.  (This facilitates the creation of add-on packages.)  The
core functionality is in the `docassemble.base` package.  With these
two packages only, you can use **docassemble** as an API.  If you do
not want to install all the packages, you can skip running compile.sh
and simply run `python setup.py install` in each of the packages you
wish to install.

The `docassemble.mako` package contains a version of [Mako] with some
minor changes needed for **docassemble** to ask the right questions in
the right order.

The `docassemble.webapp` package contains the standard docassemble web
application.  The `docassemble.demo` package contains a demonstration
interview.

# Setting up the web server

The following instructions assume a Debian/Ubuntu system on which you
have cloned `docassemble` into your home directory.  You may have to
make some changes to adapt this to your server.

Enable the Apache wsgi and xsendfile modules if they are not already enabled:

{% highlight bash %}
sudo a2enmod wsgi
sudo a2enmod xsendfile
{% endhighlight %}

Create a directory for the WSGI file:

{% highlight bash %}
sudo mkdir -p /usr/share/docassemble/webapp
{% endhighlight %}

Copy the WSGI file to this directory:

{% highlight bash %}
sudo cp ~/docassemble/docassemble_webapp/docassemble.wsgi /usr/share/docassemble/webapp
{% endhighlight %}

Set up and edit the [configuration] file, the standard location of
which is `/usr/share/docassemble/config.yml`:

{% highlight bash %}
sudo cp ~/docassemble/docassemble_base/config.yml /usr/share/docassemble/
sudo vi /usr/share/docassemble/config.yml
{% endhighlight %}

At the very least, you should edit the `secretkey` value to something
random and unique to your site.

Make sure that everything can be read and written by the web server:

{% highlight bash %}
sudo chown -R www-data.www-data /usr/share/docassemble
{% endhighlight %}

The [configuration] file needs to be readable and writeable by the web
server so that you can edit it through the web application.

Set `/etc/apache2/sites-available/000-default.conf` to something like
the following:

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
    XSendFilePath /tmp
    WSGIDaemonProcess docassemble.webserver user=www-data group=www-data threads=5
    WSGIScriptAlias /da /usr/share/docassemble/webapp/docassemble.wsgi
    <Directory /usr/share/docassemble/webapp>
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

Set `/etc/apache2/conf-available/docassemble.conf` to:

{% highlight text %}
WSGIPythonHome /usr/share/docassemble/local
{% endhighlight %}

This instructs Apache to use your [Python virtual environment] when
running the WSGI application.  Enable this by running:

{% highlight text %}
sudo a2enconf docassemble
{% endhighlight %}

Of course, you can run `docassemble` on HTTP rather than HTTPS if you
want to, but since the `docassemble` web application uses a password
system, and end users' answers to questions may be confidential, it is
a good idea to run **docassemble** on HTTPS.  If you want to run
**docassemble** on HTTP, copy the `WSGIDaemonProcess` line, the
`WSGIScriptAlias` line, and the `Directory` section into the
`<VirtualHost *:80>` section of your Apache configuration file.

If your **docassemble** interviews are not thread-safe, for example
because different interviews use different locales, change `threads=5`
to `processes=5 threads=1`.  This will cause Apache to run WSGI in a
"prefork" configuration.  This is slower than the multi-thread
configuration.  See [functions] for more information about
**docassemble** and thread safety.

`docassemble` uses a SQL database.  Set up the database by running the
following commands.  (You may wish to make changes to the database
information in the [configuration] file first.  Note that this file
will need to be readable by the `postgres` user.)

{% highlight bash %}
sudo chmod og+r /usr/share/docassemble/config.yml
echo 'create role "www-data" login; create database docassemble;' | sudo -u postgres psql
sudo -u postgres -s -- "source /usr/share/docassemble/local/bin/activate && 
python -m docassemble.webapp.create_tables"
echo 'grant all on all tables in schema public to "www-data"; grant all on all sequences in schema public to "www-data";' | sudo -u postgres psql docassemble
{% endhighlight %}

(If you store your [configuration] file in a non-standard location,
the `docassemble.webapp.create_tables` module can take a configuration
file as an argument.)

To obtain the full benefit of **docassemble**, you will need to obtain
IDs and secrets for the web services that **docassemble** uses, which
you supply to **docassemble** by editing the
[configuration] file.  In order
for the "Sign in with Google" and "Sign in with Facebook" buttons to
work, you will need to register your site on
[Google Developers Console](https://console.developers.google.com/)
and on [Facebook Developers](https://developers.facebook.com/) and .
You may also wish to obtain developer keys for the
[Google Maps Geocoding API] and for [VoiceRSS] text-to-speech
conversion.

The [configuration] file also contains settings for connecting to a
mail server.

Finally, restart Apache:

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
end, so you can edit the [configuration] to point to another type of
database system, if supported by [SQLAlchemy].  **docassemble** does
not do fancy things with SQL, so most backends should work without a
problem.  Any backend used must support column definitions with
`server_default=db.func.now()`.

# Upgrading docassemble

To upgrade docassemble to the latest version, do the following as
`www-data`:

{% highlight bash %}
cd docassemble
git pull
sudo ./compile.sh && touch /usr/share/docassemble/docassemble.wsgi
{% endhighlight %}

Note that after making changes to docassemble interviews and Python
code, it is not necessary to restart Apache.  Changing the
modification time of `/usr/share/docassemble/docassemble.wsgi` will
trigger Apache to restart the WSGI processes.

# Debugging the web app

If you get a standard Apache error message, look in
`/var/log/apache2/error.log`.  If you get an abbreviated message, the
error message could be in `/tmp/flask.log`.  Usually, however, the error
message will appear in the web browser.  To get the context of an
error, log in as a developer and check the Logs from the main menu.
The main **docassemble** log file is in
`/usr/share/docassemble/log/docassemble.log`.

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
[scalability]: {{ site.baseurl }}/docs/scalability.html
[Python virtual environment]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[pip]: https://pip.pypa.io/en/stable/
[Debian]: https://www.debian.org/
[Amazon EC2]: https://aws.amazon.com/ec2/
[Python]: https://www.python.org/
[GitHub]: https://github.com/jhpyle/docassemble
[functions]: {{ site.baseurl }}/docs/functions.html
[VoiceRSS]: http://www.voicerss.org/
[Google Maps Geocoding API]: https://developers.google.com/maps/documentation/geocoding/intro
