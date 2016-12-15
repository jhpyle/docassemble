---
layout: docs
title: How to install docassemble
short_title: Installation
---

If you are only interested in seeing how **docassemble** works, you do
not need to worry about installing it; you can run a [demonstration]
on-line instead of installing **docassemble**.

# Just use Docker

If you just want to try out running an instance of **docassemble**, it
is strongly recommended that you [install it using Docker] rather than
follow the installation instructions on this page.  If you do not
already have [Docker], you can install [Docker] on your machine
whether you have a Mac, a PC, or a Linux machine.

For example, on a Windows 10 machine, once you install
[Docker for Windows], you simply go to Windows PowerShell and type:

{% highlight bash %}
docker run -d -p 80:80 jhpyle/docassemble
{% endhighlight %}

Then, after a few minutes, the application will be available in your
browser at http://localhost.

Even if you want to put **docassemble** into production, it is
recommended that you [install it using Docker] -- ideally on an [EC2]
virtual machine hosted by [Amazon Web Services].  **docassemble**
integrates nicely with [AWS] services such as [S3] for persistent
storage.

The primary reason you might want to install **docassemble** manually
on a machine is if you want it to run on a server for which the HTTP
and HTTPS ports are serving other applications.  ([Docker] can only
use the HTTP and HTTPS ports if it has exclusive use of them.)

# Supported platforms

The installation instructions in this section assume you are
installing **docassemble** into a 64 bit [Debian]/[Ubuntu] environment
(not using [Docker]).  However, **docassemble** has been developed to
be operating-system-independent.  If you can install the dependencies,
and you know what you're doing, you should be able to get
**docassemble** to run on any operating system, with appropriate
adjustments to the [configuration].  **docassemble** has not been
tested on Mac or Windows, but all the dependencies are likely to be
available for installation on those platforms.  (E.g., see [MacTex]
for LaTeX on Mac, and [MiKTeX] for LaTeX on Windows.)

For instructions on installing **docassemble** in a multi-server
arrangement, see the [scalability] section.

# Overview of application structure

Although **docassemble** is a [Python] application, it requires more
than a `pip install` to install.

There is a core [Python] module, [`docassemble.base`], that parses
interviews and determines what question should be asked next, and
there is a separate [Python] module, [`docassemble.webapp`], that
contains the code for the web application and the
[text messaging interface].  These modules have a number of
dependencies, including other [Python] packages as well as libraries
needed by those [Python] packages

For all of the features of **docassemble** to be available, several
other applications need to run concurrently on the same server.  These
applications include:

* A web server (using ports 80 and/or 443);
* A [web sockets] background process (using port 5000);
* A [Celery] background process;
* A [cron] background process that invokes **docassemble** scripts at
hourly, daily, weekly, and monthly intervals;
* A watchdog background process that terminates any web application
processes that are stuck in an infinite loop; and
* A [Supervisor] background process (using port 9001) that
  orchestrates these functions.

In addition, the following services need to be available, either on
the same server or on a central server on the same local area network:

* A SQL server;
* A [Redis] server (port 6379) (multiple databases of which are used); and
* A [RabbitMQ] server (port 5672).

If you want to be able to view consolidated log files when you use a
[multi-server arrangement], a central log server needs to run, and
**docassemble** application servers need to run [syslog-ng] background
processes that push log file entries to that central server.

(Installing on [Docker] ensures that all of these additional
applications are running.)

It is highly recommended that you run **docassemble** over HTTPS,
since the web application uses a password system, and because your
users' answers to interview questions may be confidential.  (The
[Docker] startup process can be configured to use [Let's Encrypt] and
to automatically renew the SSL certificates.)

Finally, some of **docassemble**'s features depend on the following
services:

* An SMTP server for sending e-mails;
* [Twilio] for receiving text messages, sending text messages, and
  forwarding phone calls; and
* [VoiceRSS] for converting text to an audio file.

The authentication keys for these services can be set up in the
[configuration].

# Installing underlying packages

Before installing packages, update the package lists.

{% highlight bash %}
sudo apt-get update
{% endhighlight %}

The following [dependencies] can be installed from [Debian] or
[Ubuntu] packages:

{% highlight bash %}
sudo apt-get install apt-utils tzdata python python-dev wget unzip \
  git locales pandoc texlive texlive-latex-extra apache2 postgresql \
  libapache2-mod-wsgi libapache2-mod-xsendfile poppler-utils \
  libffi-dev libffi6 imagemagick gcc supervisor \
  libaudio-flac-header-perl libaudio-musepack-perl libmp3-tag-perl \
  libogg-vorbis-header-pureperl-perl make perl libvorbis-dev \
  libcddb-perl libinline-perl libcddb-get-perl libmp3-tag-perl \
  libaudio-scan-perl libaudio-flac-header-perl \
  libparallel-forkmanager-perl libav-tools autoconf automake \
  libjpeg-dev zlib1g-dev libpq-dev logrotate tmpreaper cron pdftk \
  fail2ban libxml2 libxslt1.1 libxml2-dev libxslt1-dev \
  libcurl4-openssl-dev libssl-dev redis-server rabbitmq-server \
  libreoffice libtool libtool-bin pacpl syslog-ng rsync s3cmd \
  curl mktemp dnsutils
{% endhighlight %}

**docassemble** depends on version 5.0.1 or later of the
[Perl Audio Converter] to convert uploaded sound files into other
formats.  If your distribution offers an earlier version, you will
need to install [pacpl] it from the source:

{% highlight bash %}
apt-get -q -y remove pacpl
git clone git://git.code.sf.net/p/pacpl/code pacpl-code 
cd pacpl-code
./configure
make
sudo make install
cd ..
{% endhighlight %}

(Note that the standard [pacpl] was installed and then uninstalled; this
ensures that [pacpl]'s dependencies exist on the system.)

**docassemble** also depends on [Pandoc] version 1.17 or later.  If
your Linux distribution provides an earlier version, you can install
from the source:

{% highlight bash %}
wget https://github.com/jgm/pandoc/releases/download/1.17.1/pandoc-1.17.1-2-amd64.deb
sudo dpkg -i pandoc-1.17.1-2-amd64.deb
{% endhighlight %}

**docassemble** uses locale settings to format numbers, get currency
symbols, and other things.  Do `echo $LANG` to see what locale you are
using.  If it is not something like `en_US.UTF-8`, you will want to
set up an appropriate locale for your region:

{% highlight bash %}
sudo dpkg-reconfigure locales
{% endhighlight %}

The [Docker] setup process does the following, which works unattended:

{% highlight bash %}
echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
update-locale LANG=en_US.UTF-8
{% endhighlight %}

On [Ubuntu], you may need to do `sudo apt-get install
language-pack-en` (or other package appropriate for your locale).

# Installing **docassemble** itself

The recommended way to install **docassemble** is to create a
[Python virtual environment] with ownership permissions set to the web
server user (`www-data` on [Debian]/[Ubuntu]), and to install
**docassemble** and its [Python] dependencies into this virtual
environment using [pip].

There are two reasons for this.  First, if the ownership of the
directories and files is set to `www-data`, developers will be able to
install and upgrade [Python] packages [through the web interface],
rather than on the command line.  Second, installing with `pip` into a
virtual environment will ensure that all of the [Python] packages are
the latest version; the versions that are packaged with Linux
distributions are not always current.

The installation process will require you to be able to run commands
as `www-data`.  By default, your system may prevent the `www-data`
user from using a shell.  You can get around this by running the
following:

{% highlight bash %}
sudo chsh -s /bin/bash www-data
sudo chown -R www-data.www-data /var/www
{% endhighlight %}

Before setting up the [Python virtual environment], you need to create
directories needed by [pip] for temporary files, and the directories in
which **docassemble** and the [Python virtual environment] will live:

{% highlight bash %}
sudo mkdir -p \
  /var/www/.pip \
  /var/www/.cache \
  /usr/share/docassemble/local \
  /usr/share/docassemble/certs \
  /usr/share/docassemble/backup \
  /usr/share/docassemble/config \
  /usr/share/docassemble/webapp \
  /usr/share/docassemble/files \
  /usr/share/docassemble/log
sudo chown -R www-data.www-data /var/www /usr/share/docassemble
{% endhighlight %}

The **docassemble** application itself is on [GitHub].  Clone the
repository (e.g., in your home directory):

{% highlight bash %}
git clone {{ site.github.repository_url }}
{% endhighlight %}

This creates a directory called `docassemble` in the current
directory.

There are four packages in the git repository:

1. <a name="docassemble"></a>[`docassemble`]: an empty namespace package;
2. <a name="docassemble.base"></a>[`docassemble.base`]: the core functionality;
3. <a name="docassemble.webapp"></a>[`docassemble.webapp`]: the web application framework; and
4. <a name="docassemble.demo"></a>[`docassemble.demo`]: a demonstration interview package

The `docassemble` package is empty because it is a "namespace"
package.  (This facilitates the use of user-created add-on packages.)
The core functionality of parsing interviews is in the
`docassemble.base` package.  With these two packages only, you can use
**docassemble** through its [Python] API.  The `docassemble.webapp`
package contains the standard **docassemble** web application, and the
`docassemble.demo` package contains a [demonstration] interview.

<a name="virtualenv"></a>To install **docassemble** and its [Python]
dependencies into the [Python virtual environment], first install the
latest version of `pip`, then install the `virtualenv` module:

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

The [ndg-httpsclient] module, which is a dependency, is installed by
itself because errors have occurred during installation when this
package does not already exist on the system.  Also note that there is
one [Python] dependency, [PyRTF-ng], which is not available on [PyPI],
but must be installed from [GitHub].

Then, you need to move certain files into place for the web
application (still acting as `www-data`):

{% highlight bash %}
cp ./docassemble/docassemble_webapp/docassemble.wsgi /usr/share/docassemble/webapp/
cp ./docassemble/Docker/config/* /usr/share/docassemble/config/
cp ./docassemble/Docker/*.sh /usr/share/docassemble/webapp/
{% endhighlight %}

The `docassemble.wsgi` file is the primary "executable" for the web
application.  Your web server configuration will point to this file.

The files copied to `/usr/share/docassemble/config/` are necessary for
[supervisor] to operate.

The `.sh` files are scripts for running background processes.

You can stop being `www-data` now:

{% highlight bash %}
exit
{% endhighlight %}

As a superuser, move the following system files into place:

{% highlight bash %}
sudo cp ./docassemble/Docker/docassemble.logrotate /etc/logrotate.d/docassemble
sudo cp ./docassemble/Docker/cron/docassemble-cron-monthly.sh /etc/cron.monthly/docassemble
sudo cp ./docassemble/Docker/cron/docassemble-cron-weekly.sh /etc/cron.weekly/docassemble
sudo cp ./docassemble/Docker/cron/docassemble-cron-daily.sh /etc/cron.daily/docassemble
sudo cp ./docassemble/Docker/cron/docassemble-cron-hourly.sh /etc/cron.hourly/docassemble
sudo cp ./docassemble/Docker/docassemble.conf /etc/apache2/conf-available/
sudo cp ./docassemble/Docker/docassemble-site.conf /etc/apache2/sites-available/docassemble.conf
sudo cp ./docassemble/Docker/docassemble-supervisor.conf /etc/supervisor/conf.d/docassemble.conf
{% endhighlight %}

The `/etc/apache2/conf-available/docassemble.conf` file contains
instructions for [Apache] to use the virtual environment to run the
**docassemble** web application.  The
`/etc/apache2/sites-available/docassemble.conf` file contains [Apache]
site configuration directives for the **docassemble** web application.

# Setting up the web application

Enable the [Apache] [wsgi], [xsendfile], [rewrite], [proxy], [proxy_http],
and [proxy_wstunnel] modules, if they are not already enabled, by
running the following:

{% highlight bash %}
sudo a2enmod wsgi
sudo a2enmod xsendfile
sudo a2enmod rewrite
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel
{% endhighlight %}

Set up and edit the [configuration] file, the standard location of
which is `/usr/share/docassemble/config.yml`:

{% highlight bash %}
sudo cp ~/docassemble/docassemble_base/config.yml /usr/share/docassemble/config/config.yml
sudo vi /usr/share/docassemble/config/config.yml
{% endhighlight %}

At the very least, you should edit the `secretkey` and
`password_secretkey` values and set them to something random and
unique to your site.  By default, **docassemble** is available at the
root of your site.  That is, if your domain is `example.com`,
**docassemble** will be available at `http://example.com` or
`https://example.com`.  If you would like it to be available at
`http://example.com/docassemble`, you will need to change the [`root`]
directive to `/docassemble/` and the [`url root`] directive to
`http://example.com/docassemble`.

Make sure that everything in the **docassemble** directory can be read
and written by the web server:

{% highlight bash %}
sudo chown -R www-data.www-data /usr/share/docassemble
{% endhighlight %}

The [configuration] file needs to be readable and writeable by the web
server so that you can edit it through the web application.

Then, edit the [Apache] site configuration and make any changes you
need to make so that **docassemble** can coexist with your other web
applications.  You should edit at least the `ServerAdmin` and
`ServerName` lines.  If you changed the [`root`] directive in the
[configuration], edit the `WSGIScriptAlias` lines in the [Apache] site
configuration.

{% highlight bash %}
sudo vi /etc/apache2/sites-available/docassemble.conf
{% endhighlight %}

If your **docassemble** interviews are not thread-safe, for example
because different interviews on your server use different locales,
change `threads=5` to `processes=5 threads=1`.  This will cause
[Apache] to run [WSGI] in a "prefork" configuration.  This is slower
than the multi-thread configuration.  See [`update_locale()`] for more
information about **docassemble** and thread safety.

Note that the HTTPS part of the configuration refers to SSL
certificates located in `/etc/ssl/docassemble/`.  If you do not have
certificates yet, you can put some self-signed certificates there,
just so [Apache] doesn't fail to start for the reason that these files
are non-existent:

{% highlight bash %}
sudo mkdir -p /etc/ssl/docassemble/
sudo cp ./docassemble/Docker/ssl/* /etc/ssl/docassemble/
{% endhighlight %}

Finally, enable the [Apache] configuration files that you installed
earlier.

{% highlight bash %}
sudo a2enconf docassemble
sudo a2ensite docassemble
{% endhighlight %}

If you did not change the [`root`] directive in the [configuration],
you should make sure the default [Apache] site configuration is
disabled, or else it will conflict with the **docassemble** site
configuration:

{% highlight bash %}
sudo a2dissite 000-default
{% endhighlight %}

Note that the [Apache] configuration file will forward HTTP to HTTPS
if the ssl [Apache] module is installed, but will run **docassemble**
solely on HTTP otherwise.  Therefore, if you wish to use HTTPS, run

{% highlight text %}
sudo a2enmod ssl
{% endhighlight %}

and if you wish to use plain HTTP, run

{% highlight text %}
sudo a2dismod ssl
{% endhighlight %}

# <a name="setup"></a>Setting up the SQL server

`docassemble` uses a SQL database.  These instructions assume you are
using [PostgreSQL] locally.  Set up the database by running the
following commands.

{% highlight bash %}
echo "create role docassemble with login password 'abc123'; create database docassemble owner docassemble;" | sudo -u postgres psql
sudo -H -u www-data bash -c "source /usr/share/docassemble/local/bin/activate && python -m docassemble.webapp.create_tables"
{% endhighlight %}

Note that these commands create a "role" in the [PostgreSQL] server
called `docassemble` with the password `abc123`, and note that the
[configuration] file, `/usr/share/docassemble/config/config.yml`,
contains these same values under the [`db`] directive.

(If you decide to store your [configuration] file in a location other
than `/usr/share/docassemble/config/config.yml`, the
`docassemble.webapp.create_tables` module will take the configuration
file path as a command line argument.)

# Setting up the log server

If you are only running **docassemble** on a single machine, you do
not need to worry about operating a central log server, and you can
skip this section.

If the machine will function as a central log server, however, you
would do the following as `root`:

{% highlight bash %}
cp ./docassemble/Docker/cgi-bin/index.sh /usr/lib/cgi-bin/
cp ./docassemble/Docker/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
{% endhighlight %}

Other machines besides the machine running the log server would push
log file entries to the central log server.  Configure this by doing:

{% highlight bash %}
cp ./docassemble/Docker/apache.logrotate /etc/logrotate.d/apache2
cp ./docassemble/Docker/docassemble-syslog-ng.conf /etc/syslog-ng/conf.d/docassemble
{% endhighlight %}

Then, you will need to edit /etc/syslog-ng/conf.d/docassemble to
replace `` `LOGSERVER` `` in the second to last line with the address of
the log server:

{% highlight yaml %}
destination d_net { tcp("log.example.local" port(514) log_fifo_size(1000)); };
{% endhighlight %}

# Connecting to other external services

To obtain the full benefit of **docassemble**, you will need to obtain
IDs and secrets for the web services that **docassemble** uses, which
you supply to **docassemble** by editing the
[configuration] file.  In order
for the "Sign in with Google" and "Sign in with Facebook" buttons to
work, you will need to register your site on
[Google Developers Console](https://console.developers.google.com/)
and on [Facebook Developers](https://developers.facebook.com/).
You may also wish to obtain developer keys for the
[Google Maps Geocoding API] and for [VoiceRSS] text-to-speech
conversion.

The [configuration] file also contains settings for connecting to a
mail server.

# Start the server and background processes

Before starting **docassemble**, make sure that [Redis] and [RabbitMQ]
are already running.

To check [Redis], do:

{% highlight bash %}
redis-cli ping
{% endhighlight %}

If it does not respond with `PONG`, then there is a problem with [Redis].

To check [RabbitMQ], do:

{% highlight bash %}
sudo rabbitmqctl status
{% endhighlight %}

If it responds with "Error: unable to connect to node . . ." then
there is a problem with [RabbitMQ].

Finally, restart [Apache] and [supervisor]:

{% highlight bash %}
sudo /etc/init.d/apache2 restart
sudo /etc/init.d/supervisor restart
{% endhighlight %}

or, if you use systemd:

{% highlight bash %}
sudo systemctl restart apache2.service
sudo systemctl restart supervisor.service
{% endhighlight %}

You will find **docassemble** running at http://example.com/da.

# Debugging problems

Log files to check include:

* `/var/log/supervisor/initialize-stderr*` (filename is different
every time)
* Files in `/var/log/supervisor` for other background processes
* `/var/log/apache2/error.log`
* `/usr/share/docassemble/log/docassemble.log`
* `/tmp/flask.log`

If you get an error in the browser that looks like a standard [Apache]
error message, look in `/var/log/apache2/error.log`.  If you get an
abbreviated message, the error message could be in `/tmp/flask.log`.
If there is a problem with the coding of an interview, the error
message will typically appear in the web browser.  To get the context
of an error, log in to **docassemble** as a developer and check the
Logs from the main menu.  The main **docassemble** log file is in
`/usr/share/docassemble/log/docassemble.log`.

The primary [supervisor] process is the one called `initialize`.  It
runs the script `/usr/share/docassemble/webapp/initialize.sh`, which
in turn launches other [supervisor] processes as necessary.  This
script is designed to be used on systems where [supervisor] serves as
a substitute for [SysV], [systemd], or other "init" system, but it is
also designed to be work correctly on systems where the "init" system
has already started some of the necessary background processes, such
as [Apache], and [PostgreSQL], [redis], and [RabbitMQ].

You can run `supervisorctl status` to see which processes `supervisor`
is controlling.  You can run `ps ax` to see which processes are
actually running.

When **docassemble** is working, you should see processes like the
following in the output of `ps ax`.

[supervisor] looks like this:

{% highlight text %}
 2121 ?        Ss     0:00 /usr/bin/python /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
 2131 ?        S      0:00 bash /usr/share/docassemble/webapp/initialize.sh
{% endhighlight %}

[cron] looks like this:

{% highlight text %}
  518 ?        Ss     0:00 /usr/sbin/cron -f
{% endhighlight %}

[redis] looks like this:

{% highlight text %}
  722 ?        Ssl    0:01 /usr/bin/redis-server 127.0.0.1:6379
{% endhighlight %}

[RabbitMQ] looks like this:

{% highlight text %}
  573 ?        S      0:00 /bin/sh -e /usr/lib/rabbitmq/bin/rabbitmq-server
  808 ?        Sl     0:06 /usr/lib/erlang/erts-7.3.1.2/bin/beam.smp -W w -A 64 -P 1048576 -K true -B i -- -root /usr/lib/erlang -progname erl -- -home /var/lib/rabbitmq -- etc. etc.
{% endhighlight %}

[PostgreSQL] looks like this:

{% highlight text %}
  778 ?        S      0:00 /usr/lib/postgresql/9.5/bin/postgres -D /var/lib/postgresql/9.5/main -c config_file=/etc/postgresql/9.5/main/postgresql.conf
  787 ?        Ss     0:00 postgres: checkpointer process
  788 ?        Ss     0:00 postgres: writer process
  789 ?        Ss     0:00 postgres: wal writer process
  790 ?        Ss     0:00 postgres: autovacuum launcher process
  791 ?        Ss     0:00 postgres: stats collector process
{% endhighlight %}

[Apache] looks like this:

{% highlight text %}
 2394 ?        S      0:00 /bin/sh /usr/sbin/apache2ctl -DFOREGROUND
 2396 ?        S      0:00 /usr/sbin/apache2 -DFOREGROUND
 2397 ?        S      0:00 /usr/sbin/apache2 -DFOREGROUND
 2398 ?        Sl     0:00 /usr/sbin/apache2 -DFOREGROUND
 2399 ?        Sl     0:00 /usr/sbin/apache2 -DFOREGROUND
 2400 ?        Sl     0:00 /usr/sbin/apache2 -DFOREGROUND
{% endhighlight %}

The [Celery] background process looks like this:

{% highlight text %}
 2343 ?        S      0:00 bash /usr/share/docassemble/webapp/run-celery.sh
 2348 ?        S      0:01 /usr/share/docassemble/local/bin/python /usr/share/docassemble/local/bin/celery worker -A docassemble.webapp.worker --loglevel=INFO
 2355 ?        S      0:00 /usr/share/docassemble/local/bin/python /usr/share/docassemble/local/bin/celery worker -A docassemble.webapp.worker --loglevel=INFO
 2356 ?        S      0:00 /usr/share/docassemble/local/bin/python /usr/share/docassemble/local/bin/celery worker -A docassemble.webapp.worker --loglevel=INFO
 2357 ?        S      0:00 /usr/share/docassemble/local/bin/python /usr/share/docassemble/local/bin/celery worker -A docassemble.webapp.worker --loglevel=INFO
 2358 ?        S      0:00 /usr/share/docassemble/local/bin/python /usr/share/docassemble/local/bin/celery worker -A docassemble.webapp.worker --loglevel=INFO
{% endhighlight %}

The [web sockets] background process looks like this:

{% highlight text %}
 2377 ?        S      0:00 bash /usr/share/docassemble/webapp/run-websockets.sh
 2378 ?        S      0:00 su -c source /usr/share/docassemble/local/bin/activate && python -m docassemble.webapp.socketserver www-data
 2382 ?        Ss     0:00 bash -c source /usr/share/docassemble/local/bin/activate && python -m docassemble.webapp.socketserver
 2387 ?        S      0:00 python -m docassemble.webapp.socketserver
{% endhighlight %}

Note that the **docassemble** web application may appear to be
functional even when [cron], [RabbitMQ], [Celery], and [web sockets]
fail to start.  This is because [cron] only matters if your interviews
use [scheduled tasks], [RabbitMQ] and [Celery] only come into play
when interviews use [background processes], and [web sockets] only
come into play when the [live help] features are used.  If you want a
fully-functional **docassemble**, you will need to make sure that all
of these services are running.

If you need to run [Python] commands like `pip` in order to fix
problems, you need to let the shell know about the virtual
environment.  You can do this by first running:

{% highlight bash %}
source /usr/share/docassemble/local/bin/activate
{% endhighlight %}

If you encounter any errors, please register an "issue" on the
**docassemble** [issues page]({{ site.github.repository_url }}/issues).

# Using different web servers and/or SQL database backends

**docassemble** is not dependent on [Apache] or [PostgreSQL].  Other web
servers that can host Python [WSGI] applications (e.g., [nginx] with
[uWSGI]) could be used.

**docassemble** uses [SQLAlchemy] to communicate with the SQL back
end, so you can edit the [configuration] to point to another type of
database system, if supported by [SQLAlchemy].  **docassemble** does
not do fancy things with SQL, so most backends should work without a
problem.  Any backend that you use must support column definitions
with `server_default=db.func.now()`.

# Running services on different machines

You can run the SQL server, [Redis], and [RabbitMQ] services on a
different machine.  Just edit the [`db`], [`redis`], and [`rabbitmq`]
directives in the [configuration].

For instructions on installing **docassemble** in a multi-server
arrangement, see the [scalability] section.

# <a name="upgrade"></a>Upgrading **docassemble**

To upgrade a local installation of **docassemble** and its
dependencies, do the following.  (This assumes that in the past you
cloned **docassemble** into the directory `docassemble` in the current
directory.)

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
cp ./docassemble_webapp/docassemble.wsgi /usr/share/docassemble/webapp/
cp ./Docker/config/* /usr/share/docassemble/config/
cp ./Docker/*.sh /usr/share/docassemble/webapp/
python -m docassemble.webapp.fix_postgresql_tables
python -m docassemble.webapp.create_tables
exit
{% endhighlight %}

If you get any errors while upgrading with `pip`, try doing the
following first:

{% highlight bash %}
sudo su www-data
source /usr/share/docassemble/local/bin/activate
pip uninstall docassemble
pip uninstall docassemble.base
pip uninstall docassemble.demo
pip uninstall docassemble.webapp
{% endhighlight %}

Sometimes, new versions of docassemble require additional database
tables or additional columns in tables.  The
[`docassemble.webapp.fix_postgresql_tables`] module adds new columns
to existing database tables, while the
[`docassemble.webapp.create_tables`] module creates new tables.

The latter works on non-[PostgreSQL] databases, but the former does
not.  If you are running a non-[PostgreSQL] database, and you get an
error about a missing column, see the [schema] for information about
what database columns need to exist.

You can reset your database by running the following commands as root:

{% highlight bash %}
echo "drop database docassemble; create database docassemble owner docassemble;" | sudo -u postgres psql
sudo -H -u www-data bash -c "source /usr/share/docassemble/local/bin/activate && python -m docassemble.webapp.create_tables"
rm -rf /usr/share/docassemble/files/0*
{% endhighlight %}

Then, restart [Apache] and [supervisor].

{% highlight bash %}
sudo systemctl restart apache2.service
sudo systemctl restart supervisor.service
{% endhighlight %}

Other times, a **docassemble** upgrade involves changes to the
[Apache] configuration, [supervisor] configuration, or auxillary
files.  In this case, you will need to manually reinstall
**docassemble**.

[schema]: {{ site.baseurl }}/docs/schema.html
[dependencies]: {{ site.baseurl }}/docs/requirements.html
[install it using Docker]: {{ site.baseurl }}/docs/docker.html
[Docker]: {{ site.baseurl }}/docs/docker.html
[MacTex]: https://tug.org/mactex/
[MiKTeX]: http://miktex.org/download
[Nodebox English Linguistics library]: https://www.nodebox.net/code/index.php/Linguistics
[site.USER_BASE]: https://pythonhosted.org/setuptools/easy_install.html#custom-installation-locations
[configuration]: {{ site.baseurl }}/docs/config.html
[`root`]: {{ site.baseurl }}/docs/config.html#root
[`url root`]: {{ site.baseurl }}/docs/config.html#url root
[`db`]: {{ site.baseurl }}/docs/config.html#db
[`redis`]: {{ site.baseurl }}/docs/config.html#redis
[`rabbitmq`]: {{ site.baseurl }}/docs/config.html#rabbitmq
[Perl Audio Converter]: http://vorzox.wix.com/pacpl
[pacpl]: http://vorzox.wix.com/pacpl
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
[`update_locale()`]: {{ site.baseurl }}/docs/functions.html#update_locale
[VoiceRSS]: http://www.voicerss.org/
[Google Maps Geocoding API]: https://developers.google.com/maps/documentation/geocoding/intro
[wsgi]: https://modwsgi.readthedocs.org/en/develop/
[xsendfile]: https://tn123.org/mod_xsendfile/
[rewrite]: http://httpd.apache.org/docs/current/mod/mod_rewrite.html
[proxy]: https://httpd.apache.org/docs/current/mod/mod_proxy.html
[proxy_http]: https://httpd.apache.org/docs/current/mod/mod_proxy_http.html
[proxy_wstunnel]: https://httpd.apache.org/docs/current/mod/mod_proxy_wstunnel.html
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[nginx]: https://www.nginx.com/
[uWSGI]: http://uwsgi-docs.readthedocs.org/en/latest/index.html
[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[PostgreSQL]: http://www.postgresql.org/
[Amazon ECS]: https://aws.amazon.com/ecs/
[demonstration]: {{ site.baseurl }}/demo.html
[GitHub]: {{ site.github.repository_url }}
[`docassemble`]: {{ site.github.repository_url }}/tree/master/docassemble
[`docassemble.base`]: {{ site.github.repository_url }}/tree/master/docassemble_base
[`docassemble.demo`]: {{ site.github.repository_url }}/tree/master/docassemble_demo
[`docassemble.webapp`]: {{ site.github.repository_url }}/tree/master/docassemble_webapp
[`docassemble.webapp.fix_postgresql_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/fix_postgresql_tables.py
[`docassemble.webapp.create_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/create_tables.py
[VoiceRSS]: http://www.voicerss.org/
[Twilio]: https://twilio.com
[multi-server arrangement]: {{ site.baseurl }}/docs/scalability.html
[through the web interface]: {{ site.baseurl }}/docs/packages.html#updating
[Docker for Windows]: https://docs.docker.com/engine/installation/windows/
[Amazon Web Services]: https://aws.amazon.com
[AWS]: https://aws.amazon.com
[Redis]: http://redis.io/
[RabbitMQ]: https://www.rabbitmq.com/
[text messaging interface]: {{ site.baseurl }}/docs/sms.html
[web sockets]: https://flask-socketio.readthedocs.io/en/latest/
[Celery]: http://www.celeryproject.org/
[cron]: https://en.wikipedia.org/wiki/Cron
[Supervisor]: http://supervisord.org/
[Let's Encrypt]: https://letsencrypt.org/
[syslog-ng]: https://en.wikipedia.org/wiki/Syslog-ng
[Pandoc]: http://pandoc.org/
[EC2]: https://aws.amazon.com/ec2/
[S3]: https://aws.amazon.com/s3/
[scheduled tasks]: {{ site.baseurl }}/docs/scheduled.html
[SysV]: https://en.wikipedia.org/wiki/UNIX_System_V
[systemd]: https://en.wikipedia.org/wiki/Systemd
[PyRTF-ng]: https://github.com/nekstrom/pyrtf-ng
[PyPI]: https://pypi.python.org/pypi
[ndg-httpsclient]: https://pypi.python.org/pypi/ndg-httpsclient
[background processes]: {{ site.baseurl }}/docs/functions.html#background
[live help]: {{ site.baseurl }}/docs/livehelp.html
