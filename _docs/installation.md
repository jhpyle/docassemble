---
layout: docs
title: How to install docassemble
short_title: Installation
---

If you just want to try out **docassemble**, it is strongly
recommended that you [run it using Docker] rather than follow all of
these installation instructions.  If you do not already have [Docker],
you can install [Docker] on your machine whether you have a Mac, a PC,
or a Linux machine.  And if you are only interested in seeing how
**docassemble** works, you can run a [demonstration] on-line instead
of installing **docassemble**.

The installation instructions in this section assume you are
installing **docassemble** into a [Debian]/[Ubuntu] environment.
However, **docassemble** has been developed to be
operating-system-independent.  If you can install the dependencies,
and you know what you're doing, you should be able to get
**docassemble** to run.  It has not been tested on Mac or Windows, but
all the dependencies are likely to be available for installation on
those platforms (see [MacTex] for LaTeX on Mac, and [MiKTeX] for LaTeX
on Windows).

For instructions on installing **docassemble** in a multi-server
arrangement, for example on [Amazon EC2], see the [scalability]
section.  In some ways, it is less work to install **docassemble** on
[Amazon ECS] than it is to install it without [Docker] on a single
machine.

# Installing dependencies

## Underlying packages

The following [dependencies] can be installed from [Debian] or
[Ubuntu] packages:

{% highlight bash %}
sudo apt-get install python python-dev pandoc texlive texlive-latex-extra \
  gcc wget unzip git locales libjpeg-dev libpq-dev apache2 postgresql \
  libapache2-mod-wsgi libapache2-mod-xsendfile poppler-utils \
  libffi-dev libffi6 imagemagick libav-tools logrotate tmpreaper cron \
  libaudio-flac-header-perl libaudio-musepack-perl libmp3-tag-perl \
  libogg-vorbis-header-pureperl-perl perl make libvorbis-dev \
  libcddb-perl libinline-perl libcddb-get-perl libmp3-tag-perl \
  libaudio-scan-perl libaudio-flac-header-perl \
  libparallel-forkmanager-perl pdftk
{% endhighlight %}

**docassemble** depends on the most recent version of the
[Perl Audio Converter] to convert uploaded sound files into other
formats, so you will need to install it from the source:

{% highlight bash %}
git clone git://git.code.sf.net/p/pacpl/code pacpl-code 
cd pacpl-code
./configure
make
sudo make install
cd ..
{% endhighlight %}

**docassemble** uses locale settings to format numbers, get currency
symbols, and other things.  Do `echo $LANG` to see what locale you are
using.  If it is not something like `en_US.UTF-8`, you will want to
set up an appropriate locale for your region:

{% highlight bash %}
sudo dpkg-reconfigure locales
{% endhighlight %}

(On [Ubuntu], you may need to do `sudo apt-get install language-pack-en`.)

## Installing **docassemble** itself

The recommended way to install **docassemble** is to create a
[Python virtual environment] that belongs to the web server user
(`www-data` on [Debian]/[Ubuntu]), and to install **docassemble** and its
dependencies into this virtual environment using [pip].

There are two reasons for this.  First, changing ownership of the
files to `www-data` will allow developers to install new Python
packages through the web interface, without having to use the command
line.  Second, this will ensure that all of the Python packages are
the latest version; the versions that are packaged with Linux
distributions are not always current.

Before setting up the [Python virtual environment], we need to create
directories needed by [pip] for temporary files, and a directory in
which to install [Python] and its packages:

{% highlight bash %}
sudo mkdir -p /var/www/.pip /var/www/.cache /usr/share/docassemble/local
sudo chown -R www-data.www-data /var/www/.pip /var/www/.cache /usr/share/docassemble
{% endhighlight %}

In order to run commands as `www-data`, you probably need to run the
following:

{% highlight bash %}
sudo chsh -s /bin/bash www-data
sudo chown -R www-data.www-data /var/www
{% endhighlight %}

The **docassemble** application itself is on [GitHub].  Clone the
repository (e.g., in your home directory):

{% highlight bash %}
git clone https://github.com/jhpyle/docassemble
{% endhighlight %}

This creates a directory called `docassemble` in the current
directory.

There are four packages in the git repository:

1. docassemble: empty namespace package;
2. docassemble.base: core functionality;
3. docassemble.webapp: the web application framework; and
4. docassemble.demo: demonstration interview package

The `docassemble` package is empty because it is a "namespace"
package.  (This facilitates the use of user-created add-on packages.)
The core functionality of parsing interviews is in the
`docassemble.base` package.  With these two packages only, you can use
**docassemble** as an API.  The `docassemble.webapp` package contains
the standard **docassemble** web application, and the `docassemble.demo`
package contains a [demonstration] interview.

To install **docassemble** and its [Python] dependencies into the
[Python virtual environment], first install the latest version of
`pip`:

{% highlight bash %}
wget https://bootstrap.pypa.io/get-pip.py
sudo -H python get-pip.py
sudo -H pip install virtualenv
{% endhighlight %}

(If you get an "InsecurePlatformWarning," you can ignore it.)

Then, become the user `www-data`:

{% highlight bash %}
sudo su www-data
{% endhighlight %}

and run the following as `www-data`:

{% highlight bash %}
virtualenv /usr/share/docassemble/local
source /usr/share/docassemble/local/bin/activate
pip install --upgrade ndg-httpsclient
pip install 'git+https://github.com/nekstrom/pyrtf-ng#egg=pyrtf-ng' \
./docassemble/docassemble \
./docassemble/docassemble_base \
./docassemble/docassemble_demo \
./docassemble/docassemble_webapp
{% endhighlight %}

Finally, to install the [Nodebox English Linguistics library], do the
following as `www-data`:

{% highlight bash %}
cd /tmp
wget https://www.nodebox.net/code/data/media/linguistics.zip
unzip linguistics.zip -d /usr/share/docassemble/local/lib/python2.7/site-packages/
rm linguistics.zip
{% endhighlight %}

Now that you have finished installing the Python dependencies into the
virtual environment, you can stop being `www-data`:

{% highlight bash %}
exit
{% endhighlight %}

# Setting up the web server

The following instructions assume a [Debian]/[Ubuntu] system on which you
have cloned the `docassemble` git repository into your home directory.
You may have to make some changes to adapt this to your server.

Enable the [Apache] [wsgi] and [xsendfile] modules if they are not already
enabled by running the following:

{% highlight bash %}
sudo a2enmod wsgi
sudo a2enmod xsendfile
{% endhighlight %}

Create a directory for the [WSGI] file:

{% highlight bash %}
sudo mkdir -p /usr/share/docassemble/webapp
{% endhighlight %}

Copy the [WSGI] file to this directory:

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

This instructs [Apache] to use your [Python virtual environment] when
running the [WSGI] application.  Enable this by running:

{% highlight text %}
sudo a2enconf docassemble
{% endhighlight %}

Of course, you can run `docassemble` on HTTP rather than HTTPS if you
want to, but since the `docassemble` web application uses a password
system, and because your users' answers to questions may be
confidential, it is a good idea to run **docassemble** on HTTPS.  If
you want to run **docassemble** on HTTP, copy the `XSendFile` lines,
the `WSGIDaemonProcess` line, the `WSGIScriptAlias` line, and the
`Directory` section into the `<VirtualHost *:80>` section of your
[Apache] configuration file.

If your **docassemble** interviews are not thread-safe, for example
because different interviews use different locales, change `threads=5`
to `processes=5 threads=1`.  This will cause [Apache] to run [WSGI] in a
"prefork" configuration.  This is slower than the multi-thread
configuration.  See [functions] for more information about
**docassemble** and thread safety.

# Setting up the SQL server

`docassemble` uses a SQL database.  These instructions assume you are
using [PostgreSQL].  Set up the database by running the following
commands.  (You may wish to make changes to the database information
in the [configuration] file first.  Note that this file will need to
be readable by the `postgres` user.)

{% highlight bash %}
sudo chmod og+r /usr/share/docassemble/config.yml
echo 'create role "www-data" login; create database docassemble owner "www-data";' | sudo -u postgres psql
sudo -H -u www-data bash -c "source /usr/share/docassemble/local/bin/activate && python -m docassemble.webapp.create_tables"
{% endhighlight %}

(If you store your [configuration] file in a non-standard location,
note that the `docassemble.webapp.create_tables` module will take the
configuration file path as an argument.)

# Connecting to other external services

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

# Start the server

Finally, restart [Apache]:

{% highlight bash %}
sudo /etc/init.d/apache2 restart
{% endhighlight %}

or, if you use systemd:

{% highlight bash %}
sudo systemctl restart apache2.service
{% endhighlight %}

You will find **docassemble** running at http://example.com/da.

## Using different web servers and/or SQL database backends

**docassemble** is not dependent on [Apache] or [PostgreSQL].  Other web
servers that can host Python [WSGI] applications (e.g., [nginx] with
[uWSGI]) could be used.

**docassemble** uses [SQLAlchemy] to communicate with the SQL back
end, so you can edit the [configuration] to point to another type of
database system, if supported by [SQLAlchemy].  **docassemble** does
not do fancy things with SQL, so most backends should work without a
problem.  Any backend used must support column definitions with
`server_default=db.func.now()`.

# Upgrading **docassemble**

To upgrade **docassemble** and its dependencies, do the following.  (This
assumes that in the past you cloned **docassemble** into the directory
`docassemble` in the current directory.)

{% highlight bash %}
cd docassemble
git pull
sudo su www-data
source /usr/share/docassemble/local/bin/activate
pip install --upgrade \
'git+https://github.com/nekstrom/pyrtf-ng#egg=pyrtf-ng' \
./docassemble \
./docassemble_base \
./docassemble_demo \
./docassemble_webapp
exit
{% endhighlight %}

If you get any errors while upgrading, try doing the following first:

{% highlight bash %}
sudo su www-data
source /usr/share/docassemble/local/bin/activate
pip uninstall docassemble
pip uninstall docassemble.base
pip uninstall docassemble.demo
pip uninstall docassemble.webapp
{% endhighlight %}

Note that after making changes to **docassemble** interviews and Python
code, it is not necessary to restart [Apache].  Changing the
modification time of `/usr/share/docassemble/docassemble.wsgi` will
trigger [Apache] to restart the [WSGI] processes.

{% highlight bash %}
sudo touch /usr/share/docassemble/docassemble.wsgi
{% endhighlight %}

# Debugging the web app

If you get a standard [Apache] error message, look in
`/var/log/apache2/error.log`.  If you get an abbreviated message, the
error message could be in `/tmp/flask.log`.  Usually, however, the error
message will appear in the web browser.  To get the context of an
error, log in as a developer and check the Logs from the main menu.
The main **docassemble** log file is in
`/usr/share/docassemble/log/docassemble.log`.

[dependencies]: {{ site.baseurl }}/docs/requirements.html
[run it using Docker]: {{ site.baseurl }}/docs/docker.html
[Docker]: {{ site.baseurl }}/docs/docker.html
[MacTex]: https://tug.org/mactex/
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
[Ubuntu]: http://www.ubuntu.com/
[Amazon EC2]: https://aws.amazon.com/ec2/
[Python]: https://www.python.org/
[GitHub]: https://github.com/jhpyle/docassemble
[functions]: {{ site.baseurl }}/docs/functions.html
[VoiceRSS]: http://www.voicerss.org/
[Google Maps Geocoding API]: https://developers.google.com/maps/documentation/geocoding/intro
[wsgi]: https://modwsgi.readthedocs.org/en/develop/
[xsendfile]: https://tn123.org/mod_xsendfile/
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[nginx]: https://www.nginx.com/
[uWSGI]: http://uwsgi-docs.readthedocs.org/en/latest/index.html
[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[PostgreSQL]: http://www.postgresql.org/
[Amazon ECS]: https://aws.amazon.com/ecs/
[demonstration]: {{ site.baseurl }}/demo.html
