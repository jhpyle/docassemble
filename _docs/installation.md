---
layout: docs
title: How to install docassemble
short_title: Installation
---

If you are only interested in seeing how **docassemble** works, you do
not need to worry about installing it; you can run a [demonstration]
on-line instead of installing **docassemble**.

# <a name="docker"></a>Just use Docker

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
integrates nicely with [AWS] services such as [S3] and [Microsoft
Azure] services such as [Azure blob storage] for persistent storage.
It also supports [S3]-compatible object storage services.

The primary reason you might want to install **docassemble** manually
on a machine is if you want it to run on a server for which the HTTP
and HTTPS ports are serving other applications.  ([Docker] can only
use the HTTP and HTTPS ports if it has exclusive use of them.)

# <a name="minimum"></a>Minimum system requirements

A machine running **docassemble** uses about 800-900MB of RAM during
normal operation.  During software updates (running [pip]), the memory
usage can momentarily be much higher.  Therefore, it is recommended
that you only run **docassemble** on a machine with at least 4GB of
RAM.

# <a name="platforms"></a>Supported platforms

The installation instructions in this section assume you are
installing **docassemble** into a 64 bit [Debian stretch] environment
(not using [Docker]).

However, **docassemble** has been developed to be
operating-system-independent.  If you can install the dependencies,
and you know what you're doing, you should be able to get
**docassemble** to run on any operating system, with appropriate
adjustments to the [configuration].  **docassemble** has not been
tested on Mac or Windows, but all the dependencies are likely to be
available for native installation on those platforms.  (E.g., see
[MacTex] for LaTeX on Mac, and [MiKTeX] for LaTeX on Windows.)
However, it would probably take a lot of time to figure this out, and
why bother, when you can install **docassemble** on a Mac or PC using
[Docker]?.

For instructions on installing **docassemble** in a multi-server
arrangement, see the [scalability] section.

# <a name="overview"></a>Overview of application structure

Although **docassemble** is a [Python] application, it requires more
than a `pip install` to install.

There is a core [Python] module, [`docassemble.base`], that parses
interviews and determines what question should be asked next.  There
is also a separate [Python] module, [`docassemble.webapp`], that
contains the code for the web application and the
[text messaging interface].  These modules have a number of
dependencies, including other [Python] packages as well as libraries
needed by those [Python] packages.

For all of the features of **docassemble** to be available, several
other applications need to run concurrently on the same server.  These
applications include:

* A web server (using ports 80 and/or 443);
* A [WSGI] server connected with the web server;
* A [web sockets] background process (using port 5000, proxied by the
  web server);
* A [cron] background process that invokes **docassemble** scripts at
hourly, daily, weekly, and monthly intervals;
* A watchdog background process that terminates any web application
processes that are stuck in an infinite loop; and
* A [Supervisor] background process (using port 9001) that
  orchestrates these functions.

In addition, the following services need to be available, either on
the same server or on a central server on the same local area network:

* A SQL server;
* A [Redis] server (port 6379) (multiple databases of which are used);
* A [RabbitMQ] server (port 5672); and
* A [Celery] background process.

If you wish to use the [e-mail receiving] feature, an [SMTP] server
for receiving e-mails (port 25) will also need to be available on a
central server.

In addition, if you want to be able to view consolidated log files
when you use a [multi-server arrangement], a central log server needs
to be present, and the **docassemble** application servers need to run
[syslog-ng] background processes that push log file entries to that
central server.

Installing on [Docker] ensures that all of these additional
applications are running.

It is highly recommended that you run **docassemble** over HTTPS,
since the web application uses a password system, and because your
users' answers to interview questions may be confidential.  (The
[Docker] startup process can be configured to use [Let's Encrypt] and
to automatically renew the SSL certificates.)

Finally, some of **docassemble**'s features depend on the following
services:

* An [SMTP] server for [sending](#email) (as opposed to receiving)
  e-mails;
* [Twilio] for receiving text messages, sending text messages, sending
  faxes, and forwarding phone calls;
* [VoiceRSS] for converting text to an audio file;
* [Google APIs] for autocompleting addresses, normalizing addresses,
  drawing maps, translating text;
* [Google APIs] or [OneDrive APIs] for synchronizing files between the
  [Playground] and a [Google Drive]/[OneDrive] folder.

The authentication keys for these services can be set up in the
[configuration].

# <a name="packages"></a>Installing underlying packages

Before installing packages, update the package lists.

{% highlight bash %}
sudo apt-get update
{% endhighlight %}

The following dependencies can be installed from [Debian] or
[Ubuntu] packages:

{% highlight bash %}
sudo apt-get install \
apt-utils \
tzdata \
python \
python-dev \
wget \
unzip \
git \
locales \
nginx \
postgresql \
gcc \
supervisor \
s4cmd \
make \
perl \
libinline-perl \
libparallel-forkmanager-perl \
autoconf \
automake \
libjpeg-dev \
libpq-dev \
logrotate \
nodejs \
npm \
cron \
libxml2 \
libxslt1.1 \
libxml2-dev \
libxslt1-dev \
libcurl4-openssl-dev \
libssl-dev \
redis-server \
rabbitmq-server \
libtool \
libtool-bin \
syslog-ng \
rsync \
curl \
dnsutils \
build-essential \
libsvm3 \
libsvm-dev \
liblinear3 \
liblinear-dev \
libzbar-dev \
libzbar0 \
libgs-dev \
default-libmysqlclient-dev \
libgmp-dev \
python-passlib \
libsasl2-dev \
libldap2-dev \
python3 \
exim4-daemon-heavy \
python3-venv \
python3-dev \
imagemagick \
pdftk \
pacpl \
pandoc \
texlive \
texlive-luatex \
texlive-latex-recommended \
texlive-latex-extra \
texlive-font-utils \
texlive-lang-cyrillic \
texlive-lang-french \
texlive-lang-italian \
texlive-lang-portuguese \
texlive-lang-german \
texlive-lang-european \
texlive-lang-spanish \
texlive-extra-utils \
poppler-utils \
libaudio-flac-header-perl \
libaudio-musepack-perl \
libmp3-tag-perl \
libogg-vorbis-header-pureperl-perl \
libvorbis-dev \
libcddb-perl \
libcddb-get-perl \
libmp3-tag-perl \
libaudio-scan-perl \
libaudio-flac-header-perl \
ffmpeg \
tesseract-ocr-all \
libtesseract-dev \
ttf-mscorefonts-installer \
fonts-ebgaramond-extra \
ghostscript \
fonts-liberation \
cm-super \
qpdf \
wamerican \
libreoffice \
zlib1g-dev \
libncurses5-dev \
libncursesw5-dev \
libreadline-dev \
libsqlite3-dev
{% endhighlight %}

You may need to make slight changes to to the package list above,
depending on which distribution and version you are using.

The latest version of [Pandoc] can be installed by doing:

{% highlight bash %}
cd /tmp \
&& wget -q https://github.com/jgm/pandoc/releases/download/2.7.3/pandoc-2.7.3-1-amd64.deb \
&& sudo dpkg -i pandoc-2.7.3-1-amd64.deb \
&& rm pandoc-2.7.3-1-amd64.deb
{% endhighlight %}

On some systems, you may run into a situation where [LibreOffice]
fails with a "permission denied" error when run by the web server.  To
avoid this, run:

{% highlight bash %}
sudo chmod -R 777 /var/spool/libreoffice
{% endhighlight %}

The installation process will require you to be able to run commands
as `www-data`.  By default, your system may prevent the `www-data`
user from using a shell.  Get around this limitation by running the
following:

{% highlight bash %}
sudo chsh -s /bin/bash www-data
sudo chown -R www-data.www-data /var/www
{% endhighlight %}

To enable the generation of [mermaid] diagrams, you will need to
switch to being the `www-data` user:

{% highlight bash %}
sudo su www-data
{% endhighlight %}

Then run the following commands to install the `mmdc` application:

{% highlight bash %}
mkdir -p /var/www/node_modules/.bin
cd /tmp
echo '{ \"args\": [\"--no-sandbox\"] }' > ~/puppeteer-config.json
touch ~/.profile
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash
source ~/.profile
nvm install 12.6.0
npm install mermaid.cli
rm ~/.profile
{% endhighlight %}

Then, run `exit` to stop acting as `www-data`, and run the following
to make the `mmdc` command available at a standard path:

{% highlight bash %}
sudo ln -s /var/www/node_modules/.bin/mmdc /usr/local/bin/mmdc
{% endhighlight %}

To enable the use of [Azure blob storage] as a means of [data
storage], run:

{% highlight bash %}
sudo npm install -g azure-storage-cmd
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
update-locale
{% endhighlight %}

On [Ubuntu], you may need to do `sudo apt-get install
language-pack-en` (or other package appropriate for your locale).

Install the latest version of [Let's Encrypt]:

{% highlight yaml %}
cd /usr/share/docassemble
git clone https://github.com/letsencrypt/letsencrypt
{% endhighlight %}

# <a name="python"></a>Installing Python 3.6

The most recent version of [Python] compatible with **docassemble** is
Python 3.6.  If your operating system does not have Python 3.6, you
can install it as follows by running the following commands as `root`
(i.e., first run `sudo su root`):

{% highlight bash %}
cd /opt \
&& wget -O Python-3.6.9.tgz https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tgz \
&& tar -zxf Python-3.6.9.tgz \
&& rm Python-3.6.9.tgz \
&& cd Python-3.6.9 \
&& ./configure --enable-shared --enable-ipv6 --enable-loadable-sqlite-extensions --with-dbmliborder=bdb:gdbm --with-computed-gotos --without-ensurepip --with-system-expat --with-system-libmpdec --with-system-ffi --prefix=/usr \
&& make \
&& make altinstall \
&& cd /tmp
{% endhighlight %}

# <a name="docassemble"></a>Installing **docassemble** itself

The recommended way to install **docassemble** is to create a [Python
virtual environment] with ownership permissions set to the web server
user (`www-data` on [Debian]/[Ubuntu]), and to install **docassemble**
and its [Python] dependencies into this virtual environment using
[pip].

There are two reasons for this.  First, if the ownership of the
directories and files is set to `www-data`, developers will be able to
install and upgrade [Python] packages [through the web interface], and
they will not need to use the command line.  Second, installing with
[pip] into a virtual environment will ensure that all of the [Python]
packages are the latest version; the versions that are packaged with
Linux distributions are not always current.

Before setting up the [Python virtual environment], you need to create
directories needed by [pip] for temporary files and the directories in
which **docassemble** and the [Python virtual environment] will live:

{% highlight bash %}
sudo mkdir -p /etc/ssl/docassemble \
   /usr/share/docassemble/local3.6 \
   /usr/share/docassemble/certs \
   /usr/share/docassemble/backup \
   /usr/share/docassemble/config \
   /usr/share/docassemble/webapp \
   /usr/share/docassemble/files \
   /var/www/.pip \
   /var/www/.cache \
   /var/run/uwsgi \
   /usr/share/docassemble/log \
   /tmp/docassemble \
   /var/www/html/log \
sudo chown -R www-data.www-data /var/www
sudo chown www-data.www-data /var/run/uwsgi
sudo chown -R www-data.www-data \
   /tmp/docassemble \
   /usr/share/docassemble/local3.6 \
   /usr/share/docassemble/log \
   /usr/share/docassemble/files
{% endhighlight %}

The **docassemble** application itself is [on GitHub].  Clone the
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
package contains the standard **docassemble** web application (which
includes the [SMS] interface), and the `docassemble.demo` package
contains a [demonstration] interview.

<a name="virtualenv"></a>To install **docassemble** and its [Python]
dependencies into the [Python virtual environment], first install the
latest version of [pip]:

{% highlight bash %}
wget https://bootstrap.pypa.io/get-pip.py
sudo -H python get-pip.py
{% endhighlight %}

(If you get an "InsecurePlatformWarning," you can ignore it.)

Then, become the user `www-data`:

{% highlight bash %}
sudo su www-data
{% endhighlight %}

and run the following as `www-data` (i.e., first do `sudo su www-data`):

{% highlight bash %}
cd /tmp
python3.6 -m venv --copies /usr/share/docassemble/local3.6
source /usr/share/docassemble/local3.6/bin/activate
pip3 install --upgrade pip
pip3 install --upgrade \
  3to2 \
  bcrypt \
  flask \
  flask-login \
  flask-mail \
  flask-sqlalchemy \
  flask-wtf \
  s4cmd \
  uwsgi \
  passlib \
  pycryptodome \
  pycryptodomex \
  six \
  setuptools
pip3 install --upgrade \
  ./docassemble/docassemble \
  ./docassemble/docassemble_base \
  ./docassemble/docassemble_demo \
  ./docassemble/docassemble_webapp
cp ./docassemble/Docker/pip.conf /usr/share/docassemble/local3.6/
{% endhighlight %}

This will install a Python 3.6 virtual environment at
`/usr/share/docassemble/local3.6` and install **docassemble** into it.


The `pip.conf` file is necessary because it enables the use of
[GitHub] package references in the `setup.py` files of **docassemble**
extension packages.

The **docassemble** packages are installed from the cloned [GitHub]
repository.  These packages are also available on [PyPI], and could be
installed with `pip install docassemble.webapp`.

Then, you need to move certain files into place for the web
application.  Still acting as `www-data`, do:

{% highlight bash %}
cp ./docassemble/docassemble_webapp/docassemble.wsgi /usr/share/docassemble/webapp/
cp ./docassemble/Docker/config/* /usr/share/docassemble/config/
cp ./docassemble/Docker/*.sh /usr/share/docassemble/webapp/
cp ./docassemble/Docker/VERSION /usr/share/docassemble/webapp/
{% endhighlight %}

The files copied to `/usr/share/docassemble/config/` include configuration
file templates for **docassemble** and [NGINX].

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
sudo cp ./docassemble/Docker/docassemble-supervisor.conf /etc/supervisor/conf.d/docassemble.conf
sudo cp ./docassemble/Docker/ssl/* /usr/share/docassemble/certs/
sudo cp ./docassemble/Docker/rabbitmq.config /etc/rabbitmq/
{% endhighlight %}

# <a name="webapp"></a>Setting up the web application

Set up and edit the **docassemble** [configuration] file, the standard location of
which is `/usr/share/docassemble/config/config.yml`:

{% highlight bash %}
sudo cp ~/docassemble/docassemble_base/config.yml /usr/share/docassemble/config/config.yml
sudo vi /usr/share/docassemble/config/config.yml
{% endhighlight %}

At the very least, you should edit the [`secretkey`] value and set it
to something random and unique to your site.

You should set [`external hostname`] to the domain of your site (e.g.,
`assembly.example.com`) and set [`url root`] to the URL that web
browsers should use to access your site (e.g.,
`http://assembly.example.com`).

By default, **docassemble** is available at the root of your site.
That is, if your domain is `assembly.example.com`, **docassemble**
will be available at `http://assembly.example.com`.  If you would like
it to be available at `http://assembly.example.com/docassemble`, you
will need to change the [`root`] directive to `/docassemble/` and the
[`url root`] directive to `http://assembly.example.com/docassemble`.
Note that it is important to include `/` marks at both the beginning
and end of [`root`].

Make sure that files in the **docassemble** directory can be read
and written by the web server:

{% highlight bash %}
sudo chown www-data.www-data /usr/share/docassemble/config/config.yml \
  /usr/share/docassemble/webapp/docassemble.wsgi
sudo chown -R www-data.www-data /usr/share/docassemble/local3.6 \
  /usr/share/docassemble/log /usr/share/docassemble/files
sudo chmod ogu+r /usr/share/docassemble/config/config.yml
{% endhighlight %}

If you want to use HTTPS with your own certificates, set the following
in your Configuration:

{% highlight yaml %}
use https: True
{% endhighlight %}

Copy your SSL certificates to the following locations:

* `/usr/share/docassemble/certs/nginx.crt` (certificate)
* `/usr/share/docassemble/certs/nginx.key` (private key)

On startup, the [initialization script] will copy these files into
`/etc/ssl/docassemble` with the appropriate ownership and permissions.

If you do not have your own SSL certificates, set the following on
your `config.yml` file, in additional to `external hostname`:

{% highlight yaml %}
use https: True
use lets encrypt: True
lets encrypt email: admin@example.com
{% endhighlight %}

Make sure that you have edited your [DNS] so that the hostname
identified in `external hostname` maps to the machine running
**docassemble**.  During the boot process, [Let's Encrypt] will be
used to obtain certificates.

# <a name="setup"></a>Setting up the SQL server

`docassemble` uses a SQL database.  This database can be located on
the same server or a different server, but these instructions assume
you are using [PostgreSQL] locally.  Your operating system may be
using a different version of [PostgreSQL], so you may need to adjust
some of the commands in these instructions.

First, allow [PostgreSQL] connections over TCP/IP:

{% highlight yaml %}
echo "host   all   all  0.0.0.0/0   md5" >> /etc/postgresql/11/main/pg_hba.conf
echo "listen_addresses = '*'" >> /etc/postgresql/11/main/postgresql.conf
{% endhighlight %}

Then set up the database by running the following commands.

{% highlight bash %}
echo "create role docassemble with login password 'abc123'; create database docassemble owner docassemble;" | sudo -u postgres psql
sudo -H -u www-data bash -c "source /usr/share/docassemble/local3.6/bin/activate && python -m docassemble.webapp.create_tables"
{% endhighlight %}

Note that these commands create a "role" in the [PostgreSQL] server
called `docassemble` with the password `abc123`.  Note also that the
[configuration] file, `/usr/share/docassemble/config/config.yml`,
contains these same values under the [`db`] directive.

(If you decide to store your [configuration] file in a location other
than `/usr/share/docassemble/config/config.yml`, you can run
`docassemble.webapp.create_tables` by passing the the configuration
file path as the first parameter on the command line.)

# <a name="setup_log"></a>Setting up the log server

If you are only running **docassemble** on a single machine, you do
not need to worry about operating a central log server, and you can
skip this section.

If the machine will function as a central log server, then other
machines besides the machine running the log server will push log file
entries to the central log server over port 514 and access the log
files through a web server at port 8080.  Configure all of this by
doing the following as `root`:

{% highlight bash %}
cp ./docassemble/Docker/cgi-bin/index.sh /usr/lib/cgi-bin/
cp ./docassemble/Docker/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
cp ./docassemble/Docker/docassemble-log.conf.dist /etc/sites-available/docassemble-log.conf
cp ./docassemble/Docker/syslog-ng-docker.conf /etc/syslog-ng/syslog-ng.conf
cp ./docassemble/Docker/docassemble-syslog-ng.conf /etc/syslog-ng/conf.d/docassemble
cp ./docassemble/Docker/nginx.logrotate /etc/logrotate.d/nginx
{% endhighlight %}

Then, edit /etc/syslog-ng/conf.d/docassemble to replace `` `LOGSERVER`
`` in the second to last line with the address of the log server.  For
example:

{% highlight yaml %}
destination d_net { tcp("log.example.local" port(514) log_fifo_size(1000)); };
{% endhighlight %}

# <a name="setup_email"></a>Setting up the e-mail server

If you want to use the [e-mail receiving] feature, you need to set up
the e-mail server so that connects with **docassemble**.  Do the
following as `root`:

{% highlight bash %}
cp ./docassemble/Docker/config/exim4-router /etc/exim4/conf.d/router/101_docassemble
cp ./docassemble/Docker/config/exim4-filter /etc/exim4/docassemble-filter
cp ./docassemble/Docker/config/exim4-main /etc/exim4/conf.d/main/01_docassemble
cp ./docassemble/Docker/config/exim4-acl /etc/exim4/conf.d/acl/29_docassemble
cp ./docassemble/Docker/config/exim4-update /etc/exim4/update-exim4.conf.conf
update-exim4.conf
{% endhighlight %}

This causes incoming e-mails to be filtered through
`/usr/share/docassemble/webapp/process-email.sh`, which saves the
e-mail to a temporary file and then runs the
`docassemble.webapp.process_email` module on the temporary file.

Configuring the e-mail receiving feature also involves:

* Setting the MX record for your domain (e.g. `help.example.com`) so
  that e-mails sent to addresses ending with `@help.example.com` will
  be directed to the **docassemble** server.
* Setting the [`incoming mail domain`] directive in the
  [configuration] to this domain (`help.example.com`).  (But you
  can skip this step if the domain is the same as the
  [`external hostname`].)
* Editing the firewall rules protecting the **docassemble** server so
  that incoming port 25 ([SMTP]) is open.
* Ensuring that no other application on the server is using port 25.

Note that sending e-mail and receiving e-mail usually require separate
[SMTP] servers.  To set up e-mail sending, see the [`mail`] directive
in the [configuration].  (Most cloud hosting services allow servers to
receive e-mail, but restrict servers' ability to send e-mail.)

For security, you should use [TLS] to encrypt e-mail communications.
By default, **docassemble** will install self-signed certificates into
the [Exim] configuration.  You should use your own certificates that
match your [`incoming mail domain`].  To use your own certificates,
create them and copy them to:

* `/usr/share/docassemble/certs/exim.crt` (certificate)
* `/usr/share/docassemble/certs/exim.key` (private key)

On startup, the [initialization script] will copy these files into the
appropriate location (`/etc/exim4`) with the appropriate ownership and
permissions.

(Note that if you use the [Docker] single-server configuration,
**docassemble** will use [Let's Encrypt] to obtain certificates and
deploy them both for the web server and for [Exim].

# <a name="external services"></a>Connecting to other external services

To obtain the full benefit of **docassemble**, you will need to obtain
IDs and secrets for the web services that **docassemble** uses, which
you supply to **docassemble** by editing the [configuration] file.  In
order for the "Sign in with Google," "Sign in with Facebook," "Sign in
with Twitter," and "Sign in with Azure" buttons to work, you will need
to register your site on [Google Developers Console],
[Facebook Developers], [Twitter Developers] and/or [Azure Portal].

You may also wish to obtain developer keys for the
[Google Maps Geocoding API] and for [VoiceRSS] text-to-speech
conversion.

The [configuration] file also contains settings for connecting to a
mail server.

## <a name="google"></a>Setting up Google logins

To enable users to log in with their Google accounts, you need to
obtain an `id` and `secret` for use with Google's [OAuth2] interface.

* Log in to the [Google Developers Console]
* Create an OAuth 2.0 client ID.
* Note the "Client ID."  You need to set this value as the `id` in the
  [`oauth`] configuration, under `google`.
* Note also the "Client secret."  You need to set this as the `secret`
  in the [`oauth`] configuration.
* Under Authorized JavaScript origins, add the URL for your
  **docassemble** site.  (E.g. `https://docassemble.example.com`)
* Under Authorized redirect URIs, add the URL
  `https://docassemble.example.com/callback/google`.

## <a name="facebook"></a>Setting up Facebook logins

To enable users to log in with their Facebook accounts, you need to
obtain an `id` and `secret` for use with Facebook's [OAuth2] interface.

* Log in to [Facebook Developers].
* Add an app.
* Give the app a name.  Users will see this name when they are asked
  to consent to sharing of information between Facebook and your site,
  so be sure to pick a name that your users will recognize.
* Note the App ID that you are assigned.  You need to set
  this value as the `id` in the [`oauth`] configuration, under
  `facebook`.
* Note also the "App Secret."  You need to set this as the `secret` in
  the [`oauth`] configuration.
* Under Valid Oauth Redirect URIs, put in the domain of your site
  followed by `/callback/facebook`.  E.g.,
  `https://docassemble.example.com/callback/facebook`.
* Edit your **docassemble** [configuration] and update the values
  under the `facebook` part of the [`oauth`] directive so that it
  includes the `id` and the `secret` you obtained in the steps above.
  Make sure that `enable` is not set to `False`.

## <a name="twitter"></a>Setting up Twitter logins

To enable users to log in with their Twitter accounts, you need to
obtain an `id` and `secret` for use with Twitter's [OAuth] interface.

* Log in to [Twitter Developers].
* Create an app.
* Give the app a name.  Users will see this name when they are asked
  to consent to sharing of information between Twitter and your site,
  so be sure to pick a name that your users will recognize.
* Set the callback URL to the URL of your site with
  `/callback/twitter` at the end.  E.g.,
  `https://docassemble.example.com/callback/twitter`.
* Enter a Privacy Policy URL and a Terms of Service URL.  Twitter
  requires these in order to give your app access to users' e-mail
  addresses.
* Set up your app so that it requests read-only access and requests
  access to the user's e-mail address.  Without access to the user's
  e-mail, the login will generate an error.
* Note the Consumer Key.  You need to set this value as the `id` in
  the [`oauth`] configuration, under `twitter`.
* Note also the "Consumer Secret."  You need to set this as the
  `secret` in the [`oauth`] configuration.
* Edit your **docassemble** [configuration] and update the values
  under the `twitter` part of the [`oauth`] directive so that it
  includes the `id` and the `secret` you obtained in the steps above.
  Make sure that `enable` is not set to `False`.

## <a name="auth0"></a>Setting up Auth0 logins

To enable users to log in with their Auth0 accounts, you need to
obtain a `domain`, `id`, and `secret` for use with Auth0's [OAuth]
interface.

* Log in to [Auth0].
* Create an application, or edit the default application.
* Give your application a name.  Users will see this name when they
  are asked to consent to sharing of information between Auth0 and
  your site, so be sure to pick a name that your users will recognize.
* Set the Application Type to "Regular Web Application."
* Set the Token Endpoint to "Post."
* Note the Domain, Client ID, and Client Secret associated with your
  application.  You will need to set these values as the `domain`,
  `id`, and `secret` values, respectively, in the [`oauth`]
  configuration, under `auth0`.
* Under Allowed Callback URLs, enter the URL of your site with
  `/callback/auth0` at the end.  E.g.,
  `https://docassemble.example.com/callback/auth0`.
* Under Allowed Web Origins, enter the URL of your site.  E.g.,
  `https://docassemble.example.com`.
* Under Allowed Logout URLs, enter the URL of your site with
  `/user/sign-in` at the end.  E.g.,
  `https://docassemble.example.com/user/sign-in`.
* Edit your **docassemble** [configuration] and update the values
  under the `auth0` part of the [`oauth`] directive so that it
  includes the `domain`, `id`, and `secret` values you noted in the
  steps above.  Make sure that `enable` is not set to `False`.
* Also, in your [configuration], set the [`url root`] directive.

## <a name="azure"></a>Setting up Microsoft Azure logins

To enable users to log in with their Microsoft accounts, you need to
obtain an `id` and `secret` for use with Microsoft's Azure Active
Directory service.

* Log into the [Azure Portal].
* Go to the Azure Active Directory resource.
* Go to App Registrations.
* Click Add.
* Set the Name to the name you want to use for your application.  This
  is the name that your users will see when they are prompted by Azure
  to give their consent to logging in with Azure.
* Set the Sign-on URL to the URL for your site's login page.  If your
  hostname is `docassemble.example.com`, then the URL will be
  `https://docassemble.example.com/user/sign-in` (unless you have set
  a non-standard [`root`]).
* Create the Registered App and then open it.
* Find the Application ID.  You need to set this value as the `id` in
  the [`oauth`] configuration, under `azure`.
* Go into Reply URLs and add an additional Reply URL for
  `https://docassemble.example.com/callback/azure`, or whatever the URL
  for `/callback/azure` is on your site.
* Go into Keys and create a new key.  The "Key description" can be
  `docassemble` or some other name of your choosing.  The duration can
  be anything you want, but note that if the duration expires, you
  will need to edit this configuration if you want users to still be
  able to log in with Azure.
* Press save.  Then copy the value of the key you just created.  You
  need to set this value as the `secret` in the [`oauth`] configuration,
  under `azure`.
* Go into Required permissions and click Add.
* Add "Microsoft Graph" as one of the APIs.
* Under "delegated permissions," select the following:
    * Sign users in
    * Access user's data anytime
    * View users' email address
    * View users' basic profile
* Press Save.
* You may also want to edit the Properties of the "registered app" in
  order to upload a logo.
* Edit your **docassemble** [configuration] and update the values
  under the `azure` part of the [`oauth`] directive so that it
  includes the `id` and the `secret` you obtained in the steps above.
  Make sure that `enable` is not set to `False`.

## <a name="google drive"></a>Setting up Google Drive integration

To enable the [Google Drive synchronization] feature, you need to
obtain a "client ID" code and a "secret" for use with Google's
[OAuth2] interface.

When this is enabled, users on your server who have the [privileges]
of `admin` or `developer` will be able to go to their "Profile" page
and click "Google Drive synchronization" to connect their
[Google Drive] with their account on your **docassemble** server.
Users will be redirected to a special page from Google where they
will be asked if they with to give your server access to their
[Google Drive].  When a user consents to this, he or she will see a
"Sync" button in the [Playground] that, when pressed, will synchronize
the contents of the user's [Playground] with a folder on the user's
[Google Drive].

In order for users with `developer` or `admin` [privileges] to be able
to connect their accounts in this way, you will need to obtain an
OAuth 2.0 client ID and secret from Google.

* Log in to the [Google Developers Console].
* Start a "project" for your server if you do not already have one.
* Enable the [Google Drive API] for the project.
* Under "Credentials," create an OAuth client ID for a "web
  application."
* Under Authorized JavaScript origins, add the URL for your
  **docassemble** site.  (E.g. `https://docassemble.example.com`)
* Under Authorized redirect URIs, add the URL for your **docassemble**
  site, followed by `/google_drive_callback`.  E.g.,
  `https://docassemble.example.com/google_drive_callback`.
* Note the "Client ID."  You need to set this value as the `id` in the
  [`oauth`] configuration, under [`googledrive`].
* Note also the "Client secret."  You need to set this as the `secret`
  in the [`oauth`] configuration.

When you have your "Client ID" and "Client secret," go to the
[configuration] and create a [`googledrive`] directive.

After the configuration is changed and the system restarts, users with
`developer` or `admin` [privileges] will be able to go to their
"Profile" and click "Google Drive synchronization."

## <a name="onedrive"></a>Setting up OneDrive integration

To enable the [OneDrive synchronization] feature, you need to sign in
to the [Azure Portal], go to "App registrations," and register an App.
Give it a name (e.g. "Docassemble OneDrive") and set the Redirect URI
to `https://example.com/onedrive_callback`, substituting your own
server URL for `https://example.com`.

Make a note of your "Application (client) ID."

Using the sidebar, navigate to "Certificates & secrets."  Click "New
client secret."  Give it a description (e.g., "Secret for OneDrive").
Set the "Expires" to "Never" unless you want the secret to expire.

Make a note of the "Value" of the secret you just created.

Using the sidebar, navigate to "API permissions" and click "Add a
permission."  Click the box for "Microsoft Graph," then click the box
for "Application permissions."  Under "Files," check the checkbox for
`Files.ReadWrite.All`.  Under "User," check the checkbox for
`User.Read.All`.  Then click "Add permissions."

Using the sidebar, navigate to "Branding."  Upload a logo (square
image files work best) and enter URLs for your home page, terms of
service, and privacy statement.  Note that the only people who will
see these things are your developers.

Using the sidebar, navigate to "Authentication."  Under "Supported
Account Types," select "Accounts in any organization directory."  Then
press "Save."

Then, go to your [Configuration].  Edit the [`onedrive`] directive
under `oauth`.  Set the `id` to the "Application (client) ID" you
obtained earlier, and set the `secret` to the "Value" of the secret
you obtained earlier.  Note that you may need to put quotes around the
password in order to avoid [YAML] problems.

When this is enabled, users on your server who have the [privileges]
of `admin` or `developer` will be able to go to their "Profile" page
and click "OneDrive synchronization" to connect their [OneDrive] with
their account on your **docassemble** server.  Users will be
redirected to a special page from Microsoft where they will be asked
if they with to give your server access to their [OneDrive].  When a
user consents to this, he or she will see a "Sync" button in the
[Playground] that, when pressed, will synchronize the contents of the
user's [Playground] with a folder on the user's [OneDrive].

If you enable both [Google Drive synchronization] and [OneDrive
synchronization], users will be able to choose either, but not both.
Enabling one will disable the other.

## <a name="github"></a>Setting up GitHub integration

To enable the [GitHub integration] feature, you need to obtain an `id`
and `secret` so that your **docassemble** server can communicate with
[GitHub] using the [GitHub API].

When this is enabled, users on your server who have the [privileges]
of `admin` or `developer` will be able to go to their "Profile" page
and click "GitHub integration" to connect their [GitHub] account with
their account on your **docassemble** server.  Users will be
redirected to a special page on the [GitHub] web site where [GitHub]
will ask them if they want to give your "application" (your
**docassemble** server) privileges to manage repositories and SSH keys
on their [GitHub] account.  When a user consents to this, he or she
will see a "GitHub" button in the [packages folder] of the
[Playground].  Pressing this button will push a [commit] to [GitHub]
representing the current state of the code of the package.

In order for interview developers to be able to connect their accounts in
this way, you will need to register your **docassemble** server as an
"OAuth application" on [GitHub]:

* [Create an account on GitHub] if you have not done so already.
* Log in to [GitHub].
* Go to your "[Settings](https://github.com/settings/profile)."
* Navigate to
  "[Developer settings](https://github.com/settings/developers)."  The
  "[OAuth Apps](https://github.com/settings/developers)" tab should be
  active.
* Press the "Register a new application" button.
* Enter an "Application name" that describes your **docassemble**
  server.  Interview developers will see this application name when [GitHub]
  asks them if they wish to grant your server access to their [GitHub]
  account.
* Under "Homepage URL," enter the URL of your **docassemble** server.
* If you want, enter an "Application description."  Interview developers will see
  this when [GitHub] asks them if they wish to grant your server
  access to their [GitHub] account.
* Under "Authorization callback URL," enter the URL for your server
  followed by `/github_oauth_callback`.  So, if interview developers
  access the [Playground] at
  `https://docassemble.example.com/playground`, the callback URL will
  be `https://docassemble.example.com/github_oauth_callback`.  This
  setting needs to be precisely set or else the integration will not
  work.
* Press the "Register application" button.
* [GitHub] will then tell you the "Client ID" and "Client Secret" of
  your new "OAuth application."  Note the values of these codes; you
  need to plug them into your **docassemble** [configuration].
* On your **docassemble** server, go to "Configuration."  Under the
  [`oauth`] directive, and under the [`github`] sub-directive within
  [`oauth`], set `id` to the "Client ID," and set `secret` to the
  "Client Secret".  Set `enable` to `True`.

The server will restart after you change the [configuration].  Then,
when you go to your "Profile," you should see a "GitHub integration"
link.

When interview developers click this link and they choose to associate
their [GitHub] account with their account on your **docassemble**
server, **docassemble** stores an access token in [Redis] for the
user.  This allows **docassemble** to authenticate with the [GitHub
API].  **docassemble** also creates an SSH private key and an SSH
public key annotated with the e-mail address associated with the
user's [GitHub] account.  These SSH keys are stored in the same
directory in the Playground as the files for [Playground] packages, so
they will appear in [Google Drive] or [OneDrive] if [Google Drive
synchronization] or [OneDrive synchronization] is enabled, and they
will be stored in the cloud if cloud [data storage] is enabled.  Using
the [GitHub API], **docassemble** stores the public key in the user's
[GitHub] account, using the name of the application as specified in
the [configuration] as the value of [`appname`] (which defaults to
`docassemble`).  (If you are using GitHub integration from more than
one server, make sure that each server has a different [`appname`].)

When users configure their [GitHub] integration, they have two
checkboxes they can use to configure how the integration works:

* Access shared repositories
* Access organizational repositories

If "Access shared repositories" is checked, then the [GitHub]
integration will access repositories that are owned by someone else
but shared with the user.  If "Access organizational repositories" is
checked, then [GitHub] integration will access repositories that are
in the organization of the user.  If many repositories are connected
with your account, you may need to uncheck these checkboxes.

## <a name="email"></a>Setting up e-mail sending

If you plan to use the [`send_email()`] function or any other feature
that uses e-mail, you will need to set up some way to send e-mails.

Traditionally, e-mail has been sent through [SMTP] servers.  While it
is easy to deploy an [SMTP] server on a machine, most cloud providers
block outgoing [SMTP] connections as a way to limit spam.  As a
result, you will probably have to use a special service to send e-mail
through [SMTP], such as [Amazon SES], [SendGrid], [MailChimp],
[Mailgun], and [Google Apps].

You can also send e-mail without using [SMTP].  If you have a
[Mailgun] account, you can use the [Mailgun API] or the [SendGrid API]
from **docassemble** to send mail.  This avoids many of the problems
with [SMTP].  For instructions on sending e-mail this way, see the
documentation for the [`mailgun api key`] and [`sendgrid api key`]
directives in the [configuration].

However, if you want to send e-mail using [SMTP], you can use the
[`mail`] directive in the [configuration] to point **docassemble** to
an [SMTP] server.

If you have a Google account, you can use a Gmail [SMTP] server by
setting the following in your [configuration]:

{% highlight yaml %}
mail:
  server: smtp.gmail.com
  username: yourgoogleusername
  password: yourgooglepassword
  use tls: True
  port: 465
  default_sender: '"Administrator" <no-reply@example.com>'
{% endhighlight %}

For this to work, you will need to go into your [Google settings] and
set "Allow less secure apps" to "ON."  (Gmail may soon discontinue
support for using their service as an SMTP server, but the example is
still illustrative.)

Other [SMTP] services include [SendGrid], [Mailgun], [MailChimp], and
[Amazon SES].  It is also possible to use an [SMTP] server from
[Google Apps] if you have a [G Suite] account.  [SendGrid] and
[Mailgun] also offer API-based sending methods, which tend to be
faster; see the [`sendgrid api key`] and [`mailgun api key`]
configuration directives.

In order to minimize the chances that e-mail you send from these
services will be flagged as spam, you may need to spend some time
configuring [SPF] records, [DKIM] records, [reverse DNS], and the
like.

# <a name="start"></a>Start the server and background processes

First, we need to disable the automatic starting and stopping of
[NGINX] on your server.  Your server will still run [NGINX], but we
need it to be controlled by [supervisor] rather than [systemd]:

{% highlight bash %}
sudo systemctl stop nginx.service
sudo systemctl disable nginx.service
{% endhighlight %}

Do the same with [RabbitMQ]:

{% highlight bash %}
sudo systemctl stop rabbitmq-server.service
sudo systemctl disable rabbitmq-server.service
{% endhighlight %}

If you are using the [e-mail receiving] feature, disable the exim4
service as well:
{% highlight bash %}
sudo systemctl stop exim4.service
sudo systemctl disable exim4.service
{% endhighlight %}

Make sure that [Redis] is already running.  It should have started
running after installation.

To check [Redis], do:

{% highlight bash %}
redis-cli ping
{% endhighlight %}

If it does not respond with `PONG`, then there is a problem with [Redis].

Optionally, you can also control [PostgreSQL] and [Redis] with [supervisor]:

{% highlight bash %}
sudo systemctl stop postgresql.service
sudo systemctl disable postgresql.service
sudo systemctl stop redis.service
sudo systemctl disable redis.service
{% endhighlight %}

If [supervisor] controls [PostgreSQL] and [Redis], then when
[supervisor] stops, it will make a backup of the [PostgreSQL] database
and the [Redis] database in `/usr/share/docassemble/backup/` (or in
the cloud).

Alternatively, you can allow [systemd] to launch [PostgreSQL],
[Redis], and [RabbitMQ], but in this case you should make sure that
during the boot process, [supervisor] starts running after these
services have started.  To do this, run:

{% highlight bash %}
sudo systemctl edit supervisor.service
{% endhighlight %}

and enter the following into the editor:

{% highlight text %}
[Unit]
After=rabbitmq-server.target postgresql.target redis-server.target
{% endhighlight %}

Then tell [systemd] to notice your changes:

{% highlight bash %}
systemctl daemon-reload
{% endhighlight %}

Before starting [supervisor], you need to edit
`/etc/supervisor/supervisord.conf`:

{% highlight bash %}
sudo vi /etc/supervisor/supervisord.conf
{% endhighlight %}

Add the following line immediately after the
`{% raw %}[supervisord]{% endraw %}` line:

{% highlight text %}
environment=DAPYTHONVERSION="3"
{% endhighlight %}

This indicates that you will use Python 3 rather than Python 2 (which
is a default only for backwards-compatibility reasons).

To start **docassemble**, start the [supervisor] service (which may
require stopping it first):

{% highlight bash %}
sudo systemctl stop supervisor.service
sudo systemctl start supervisor.service
{% endhighlight %}

The startup process can take a lot of time.  You can monitor the
progress by running:

{% highlight bash %}
sudo supervisorctl status
{% endhighlight %}

If `initialize` has `EXITED`, there was a problem during startup.  If
`initialize` is `RUNNING`, but `nginx` hasn't started yet, the system
is still starting.

Log files for each service are written to files in
`/var/log/supervisor`.  The `initialize` process takes time because it
does a software update using [pip].  Another thing that takes a long
time is the creation of the database tables in [PostgreSQL].

After 15 minutes or so, you should find **docassemble** running at the
URL for your site.

You should change the password for the default admin user.  Click
"Sign in or sign up to save answers" or navigate to `/user/sign-in`.
Log in with:

* Email: admin@admin.com
* Password: password

It should immediately prompt you to change your password to something secure.

# <a name="debug"></a>Debugging

Run `sudo supervisorctl status` to see the status of the processes `supervisor` is
controlling.  A healthy output would look like this:

{% highlight text %}
apache2                          STOPPED   Not started
celery                           RUNNING   pid 1288, uptime 2:52:43
cron                             RUNNING   pid 1494, uptime 2:51:53
exim4                            RUNNING   pid 1504, uptime 2:51:52
initialize                       RUNNING   pid 9, uptime 2:53:55
nginx                            RUNNING   pid 1452, uptime 2:52:14
postgres                         RUNNING   pid 720, uptime 2:53:27
rabbitmq                         RUNNING   pid 1012, uptime 2:52:53
redis                            RUNNING   pid 855, uptime 2:53:04
reset                            STOPPED   Not started
sync                             STOPPED   Not started
syslogng                         STOPPED   Not started
update                           STOPPED   Not started
uwsgi                            RUNNING   pid 1395, uptime 2:52:30
watchdog                         RUNNING   pid 10, uptime 2:53:55
websockets                       RUNNING   pid 1384, uptime 2:52:32
{% endhighlight %}

In this setup, the `postgres`, `rabbitmq`, and `redis` services are
being controlled by [supervisor].  If they are controlled by [systemd]
on your server, they may show as `STOPPED`.

* If [PostgreSQL] is running, `pg_isready` should return "accepting
connections."
* If [RabbitMQ] is running, `sudo rabbitmqctl status` should run
without error.
* If [Redis] is running, `redis-cli ping` should return "PONG."

You can also run `ps ax` to see which processes are actually running.

Log files to check include:

* `/var/log/supervisor/initialize-stderr*` (filename is different
every time)
* Files in `/var/log/supervisor` for other background processes
* `/var/log/nginx/error.log`
* `/usr/share/docassemble/log/docassemble.log`
* `/usr/share/docassemble/log/uwsgi.log`
* `/tmp/flask.log`

If the `celery` process failed to start, or you are debugging
[background processes], check:

* `/usr/share/docassemble/log/worker.log`

If you are debugging [e-mail receiving], check:

* `/tmp/mail.log`
* `/var/log/exim4/mainlog`

If you get an error in the browser that looks like a standard [NGINX]
error message, look in `/usr/share/docassemble/log/uwsgi.log` and
`/var/log/nginx/error.log`.  If you get an abbreviated message, the
error message could be in `/tmp/flask.log`.  If there is a problem
with the coding of an interview, the error message will typically
appear in the web browser.  To get the context of an error, log in to
**docassemble** as a developer and check the Logs from the main menu.
The main **docassemble** log file is in
`/usr/share/docassemble/log/docassemble.log`.

Keep in mind that because of log rotation, you might find that a log
file like `/usr/share/docassemble/log/uwsgi.log` is empty, and that
the real log file is `/usr/share/docassemble/log/uwsgi.log.1`.

The primary [supervisor] process is the one called `initialize`.  It
runs the script `/usr/share/docassemble/webapp/initialize.sh`, which
in turn launches other [supervisor] processes as necessary.  This
script is designed to be used on systems where [supervisor] serves as
a substitute for [SysV], [systemd], or other "init" system, but it is
also designed to be work correctly on systems where the "init" system
has already started some of the necessary background processes, such
as [NGINX], and [PostgreSQL], [redis], and [RabbitMQ].

When **docassemble** is working, you should see processes like the
following in the output of `ps ax`.

[supervisor] looks like this:

{% highlight text %}
 2121 ?        Ss     0:00 /usr/bin/python2 /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
 2131 ?        S      0:00 bash /usr/share/docassemble/webapp/initialize.sh
{% endhighlight %}

[cron] looks like this:

{% highlight text %}
  518 ?        Ss     0:00 /usr/sbin/cron -f
{% endhighlight %}

[redis] looks like this:

{% highlight text %}
  855 ?        S      0:00 bash /usr/share/docassemble/webapp/run-redis.sh
  863 ?        Sl     0:13 redis-server 0.0.0.0:6379
{% endhighlight %}

[RabbitMQ] looks like this:

{% highlight text %}
  573 ?        S      0:00 /bin/sh -e /usr/lib/rabbitmq/bin/rabbitmq-server
  808 ?        Sl     0:06 /usr/lib/erlang/erts-10.2.4/bin/beam.smp -W w -A 64 -MBas ageffcbf -MHas ageffcbf -MBlmbcs 512 -MHlmbcs 512 -MMmcs 30 -P 1048576 -t 5000000 -stbt db -zdbbl 128000 -K true -B i -- -root /usr/lib/erlang -progname erl -- -home /var/lib/rabbitmq -- etc. etc.
{% endhighlight %}

[PostgreSQL] looks like this:

{% highlight text %}
  741 ?        S      0:00 su postgres -c /usr/lib/postgresql/11/bin/postgres -D /var/lib/postgresql/11/main -c config_file=/etc/postgresql/11/main/postgresql.conf
  742 ?        Ss     0:00 /usr/lib/postgresql/11/bin/postgres -D /var/lib/postgresql/11/main -c config_file=/etc/postgresql/11/main/postgresql.conf
  745 ?        Ss     0:00 postgres: 11/main: checkpointer
  746 ?        Ss     0:00 postgres: 11/main: background writer
  747 ?        Ss     0:00 postgres: 11/main: walwriter
  748 ?        Ss     0:00 postgres: 11/main: autovacuum launcher
  749 ?        Ss     0:00 postgres: 11/main: stats collector
  750 ?        Ss     0:00 postgres: 11/main: logical replication launcher
 1444 ?        Ss     0:00 postgres: 11/main: docassemble docassemble 127.0.0.1(37314) idle
{% endhighlight %}

[NGINX] looks like this:

{% highlight text %}
 1452 ?        S      0:00 bash /usr/share/docassemble/webapp/run-nginx.sh
 1470 ?        S      0:00 nginx: master process /usr/sbin/nginx -g daemon off;
 1471 ?        S      0:00 nginx: worker process
{% endhighlight %}

The [Celery] background process looks like this:

{% highlight text %}
 1288 ?        S      0:00 bash /usr/share/docassemble/webapp/run-celery.sh
 1295 ?        S      0:11 /usr/share/docassemble/local3.6/bin/python3.6 /usr/share/docassemble/local3.6/bin/celery worker -A docassemble.webapp.worker --loglevel=INFO
 1349 ?        S      0:00 /usr/share/docassemble/local3.6/bin/python3.6 /usr/share/docassemble/local3.6/bin/celery worker -A docassemble.webapp.worker --loglevel=INFO
{% endhighlight %}

The [web sockets] background process looks like this:

{% highlight text %}
 1384 ?        S      0:00 bash /usr/share/docassemble/webapp/run-websockets.sh
 1391 ?        S      0:06 python -u -m docassemble.webapp.socketserver
{% endhighlight %}

Note that the **docassemble** web application may appear to be
functional even when [cron], [RabbitMQ], [Celery], and [web sockets]
fail to start.  This is because [cron] only matters if your interviews
use [scheduled tasks], [RabbitMQ] and [Celery] only come into play
when interviews use [background processes], and [web sockets] only
come into play when the [live help] features are used.  If you want a
fully-functional **docassemble**, you will need to make sure that all
of these services are running.

If you need to run [Python] commands like [pip] in order to fix
problems, you need to run `su www-data` so that you are running as the
same user as [NGINX].  In addition, you need to let the shell know
about the virtual environment.  You can do this by running the
following before you run any [Python] commands:

{% highlight bash %}
source /usr/share/docassemble/local3.6/bin/activate
{% endhighlight %}

If you encounter any errors, please register an "issue" on the
**docassemble** [issues page]({{ site.github.repository_url }}/issues).

# <a name="issues"></a>Known issues

As of August 2017, harmless errors have been issuing when a script exits:

{% highlight text %}
Exception TypeError: "'NoneType' object is not callable" in <function remove at 0x7fd44df87410> ignored
Exception TypeError: "'NoneType' object is not callable" in <function remove at 0x7fd44df87410> ignored
{% endhighlight %}

This error message is caused by the `weakref` [Python] package.  It
appears to be harmless and may be fixed soon.

# <a name="backends"></a>Using different web servers and/or SQL database backends

**docassemble** needs a web server and a SQL server, but it is not
dependent on [NGINX] or [PostgreSQL].  If you would rather use
[Apache], you can install Apache and edit your
`/etc/supervisor/supervisord.conf` file to add `DAWEBSERVER="apache"`.

**docassemble** uses [SQLAlchemy] to communicate with the SQL back
end, so you can edit the [configuration] to point to another type of
database system, if supported by [SQLAlchemy].  **docassemble** does
not do fancy things with SQL, so most backends should work without a
problem.  Any backend that you use must support column definitions
with `server_default=db.func.now()`.

# <a name="othermachines"></a>Running services on different machines

You can run the SQL server, [Redis], and [RabbitMQ] services on a
different machine.  Just edit the [`db`], [`redis`], and [`rabbitmq`]
directives in the [configuration].

For instructions on installing **docassemble** in a multi-server
arrangement, see the [scalability] section.

# <a name="upgrade"></a>Upgrading **docassemble**

To see what version of **docassemble** you are running, log in as an
administrator and go to "Configuration" from the menu.  To find out
the version number of the latest available **docassemble** software,
visit to the [**docassemble** PyPI page].  The "Configuration" page
might report that the "Python" version number and the "system" version
number are different.  This may happen when you upgrade a
**docassemble** extension package: the **docassemble** [Python]
packages are dependencies and will be upgraded to the latest version
available on [PyPI], while the parts of **docassemble** that are
outside of these packages (the "system") remain as they were when you
first installed **docassemble**.  Updates to the "system" files are
rare, so it is usually not a problem for the "Python" version number
to be ahead of the "system" version number.  If there is a
compatibility issue, you will see a warning.

To upgrade a local installation of **docassemble** and its
dependencies, do the following.  (This assumes that in the past you
cloned **docassemble** into the directory `docassemble` in the current
directory.)

{% highlight bash %}
cd docassemble
git pull
sudo su www-data
source /usr/share/docassemble/local3.6/bin/activate
pip install --upgrade \
./docassemble \
./docassemble_base \
./docassemble_demo \
./docassemble_webapp
cp ./docassemble_webapp/docassemble.wsgi /usr/share/docassemble/webapp/
cp ./Docker/config/* /usr/share/docassemble/config/
cp ./Docker/*.sh /usr/share/docassemble/webapp/
cp ./Docker/VERSION /usr/share/docassemble/webapp/
python -m docassemble.webapp.create_tables
exit
{% endhighlight %}

If you get any errors while upgrading with [pip], try doing the
following first:

{% highlight bash %}
sudo su www-data
source /usr/share/docassemble/local3.6/bin/activate
pip uninstall docassemble
pip uninstall docassemble.base
pip uninstall docassemble.demo
pip uninstall docassemble.webapp
{% endhighlight %}

Sometimes, new versions of docassemble require additional database
tables or additional columns in tables.  The
[`docassemble.webapp.create_tables`] module uses [alembic] to make any
necessary modifications to the tables.

{% highlight bash %}
sudo -H -u www-data bash -c "source /usr/share/docassemble/local3.6/bin/activate && python -m docassemble.webapp.create_tables"
{% endhighlight %}

If you get an error in your logs about a missing column and running
[`docassemble.webapp.create_tables`] does not fix the problem, see the
database [schema] for information about what database columns need to
exist in the database.

You can delete and recreate your database by running the following commands as root:

{% highlight bash %}
echo "drop database docassemble; create database docassemble owner docassemble;" | sudo -u postgres psql
sudo -H -u www-data bash -c "source /usr/share/docassemble/local3.6/bin/activate && python -m docassemble.webapp.create_tables"
rm -rf /usr/share/docassemble/files/0*
{% endhighlight %}

Then, restart [supervisor].

{% highlight bash %}
sudo systemctl stop supervisor.service
sudo systemctl start supervisor.service
{% endhighlight %}

Other times, a **docassemble** upgrade involves changes to the
[Apache] configuration, [supervisor] configuration, or auxillary
files.  In this case, you will need to make the changes by hand or
manually reinstall **docassemble**.

All of these system administration headaches can be avoided by
[using Docker].

[using Docker]: {{ site.baseurl }}/docs/docker.html
[schema]: {{ site.baseurl }}/docs/schema.html
[install it using Docker]: {{ site.baseurl }}/docs/docker.html
[Docker]: {{ site.baseurl }}/docs/docker.html
[MacTex]: https://tug.org/mactex/
[MiKTeX]: http://miktex.org/download
[Nodebox English Linguistics library]: https://www.nodebox.net/code/index.php/Linguistics
[site.USER_BASE]: https://pythonhosted.org/setuptools/easy_install.html#custom-installation-locations
[configuration]: {{ site.baseurl }}/docs/config.html
[Configuration]: {{ site.baseurl }}/docs/config.html
[`root`]: {{ site.baseurl }}/docs/config.html#root
[`url root`]: {{ site.baseurl }}/docs/config.html#url root
[`external hostname`]: {{ site.baseurl }}/docs/config.html#external hostname
[`secretkey`]: {{ site.baseurl }}/docs/config.html#secretkey
[`db`]: {{ site.baseurl }}/docs/config.html#db
[`redis`]: {{ site.baseurl }}/docs/config.html#redis
[`rabbitmq`]: {{ site.baseurl }}/docs/config.html#rabbitmq
[`mail`]: {{ site.baseurl }}/docs/config.html#mail
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
[headers]: http://httpd.apache.org/docs/current/mod/mod_headers.html
[proxy_wstunnel]: https://httpd.apache.org/docs/current/mod/mod_proxy_wstunnel.html
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[uWSGI]: http://uwsgi-docs.readthedocs.org/en/latest/index.html
[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[PostgreSQL]: http://www.postgresql.org/
[Amazon ECS]: https://aws.amazon.com/ecs/
[demonstration]: {{ site.baseurl }}/demo.html
[on GitHub]: {{ site.github.repository_url }}
[GitHub]: https://github.com
[`docassemble`]: {{ site.github.repository_url }}/tree/master/docassemble
[`docassemble.base`]: {{ site.github.repository_url }}/tree/master/docassemble_base
[`docassemble.demo`]: {{ site.github.repository_url }}/tree/master/docassemble_demo
[`docassemble.webapp`]: {{ site.github.repository_url }}/tree/master/docassemble_webapp
[`docassemble.webapp.fix_postgresql_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/fix_postgresql_tables.py
[`docassemble.webapp.create_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/create_tables.py
[Twilio]: https://twilio.com
[multi-server arrangement]: {{ site.baseurl }}/docs/scalability.html
[through the web interface]: {{ site.baseurl }}/docs/packages.html#updating
[Docker for Windows]: https://docs.docker.com/engine/installation/windows/
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
[scheduled tasks]: {{ site.baseurl }}/docs/background.html#scheduled
[SysV]: https://en.wikipedia.org/wiki/UNIX_System_V
[systemd]: https://en.wikipedia.org/wiki/Systemd
[PyRTF-ng]: https://github.com/nekstrom/pyrtf-ng
[PyPI]: https://pypi.python.org/pypi
[ndg-httpsclient]: https://pypi.python.org/pypi/ndg-httpsclient
[background processes]: {{ site.baseurl }}/docs/background.html#background
[live help]: {{ site.baseurl }}/docs/livehelp.html
[SMTP]: https://en.wikipedia.org/wiki/SMTP
[Amazon SES]: https://aws.amazon.com/ses/
[Amazon Web Services]: https://aws.amazon.com
[SMS]: {{ site.baseurl }}/docs/sms.html
[data storage]: {{ site.baseurl }}/docs/docker.html#data storage
[Azure blob storage]: {{ site.baseurl }}/docs/docker.html#persistent azure
[Microsoft Azure]: https://azure.microsoft.com/en-us/
[SendGrid]: https://sendgrid.com/
[Exim]: https://en.wikipedia.org/wiki/Exim
[e-mail receiving]: {{ site.baseurl }}/docs/background.html#email
[`incoming mail domain`]: {{ site.baseurl }}/docs/config.html#incoming mail domain
[initialization script]: {{ site.github.repository_url }}/blob/master/Docker/initialize.sh
[TLS]: https://en.wikipedia.org/wiki/Transport_Layer_Security
[Azure Portal]: https://portal.azure.com
[Google Developers Console]: https://console.developers.google.com/
[Facebook Developers]: https://developers.facebook.com/
[Twitter Developers]: https://apps.twitter.com/
[OAuth2]: https://oauth.net/2/
[`oauth`]: {{ site.baseurl }}/docs/config.html#oauth
[LibreOffice]: https://www.libreoffice.org/
[certbot instructions]: https://certbot.eff.org/all-instructions/
[certbot]: https://certbot.eff.org/
[Google Drive synchronization]: {{ site.baseurl }}/docs/playground.html#google drive
[OneDrive synchronization]: {{ site.baseurl }}/docs/playground.html#onedrive
[MailChimp]: https://mailchimp.com/
[Mailgun]: https://www.mailgun.com/
[Google Apps]: https://support.google.com/a/answer/176600?hl=en
[G Suite]: https://gsuite.google.com/
[roles]: {{ site.baseurl }}/docs/roles.html
[**docassemble** PyPI page]: https://pypi.python.org/pypi/docassemble.webapp
[GitHub API]: https://developer.github.com/v3/
[Create an account on GitHub]: https://github.com/join
[packages folder]: {{ site.baseurl }}/docs/playground.html#packages
[commit]: https://git-scm.com/docs/git-commit
[Playground]: {{ site.baseurl }}/docs/playground.html
[privileges]: {{ site.baseurl }}/docs/users.html
[Google Drive API]: https://developers.google.com/drive/v3/web/about-sdk
[OneDrive API]: https://docs.microsoft.com/en-us/onedrive/developer/rest-api/
[GitHub integration]: {{ site.baseurl }}/docs/packages.html#github
[`send_email()`]: {{ site.baseurl }}/docs/functions.html#send_email
[DNS]: https://en.wikipedia.org/wiki/Domain_Name_System
[TXT record]: https://en.wikipedia.org/wiki/TXT_record
[SPF]: https://en.wikipedia.org/wiki/Sender_Policy_Framework
[DKIM]: https://en.wikipedia.org/wiki/DomainKeys_Identified_Mail
[reverse DNS]: https://en.wikipedia.org/wiki/Reverse_DNS_lookup
[submit a support request]: http://docs.aws.amazon.com/ses/latest/DeveloperGuide/request-production-access.html
[`appname`]: {{ site.baseurl }}/docs/config.html#appname
[pdfx]: https://www.ctan.org/pkg/pdfx?lang=en
[LaTeX]: https://en.wikipedia.org/wiki/LaTeX
[Debian stretch]: https://wiki.debian.org/DebianStretch
[npm]: https://www.npmjs.com
[`googledrive`]: {{ site.baseurl }}/docs/config.html#googledrive
[`onedrive`]: {{ site.baseurl }}/docs/config.html#onedrive
[pip]: https://pip.pypa.io/en/stable/
[OAuth]: https://oauth.net/1/
[alembic]: http://alembic.zzzcomputing.com/en/latest/
[`github`]: {{ site.baseurl }}/docs/config.html#github
[`server administrator email`]: {{ site.baseurl }}/docs/config.html#server administrator email
[Google APIs]: https://developers.google.com/apis-explorer/#p/
[Google Drive]: https://drive.google.com
[OneDrive]: https://onedrive.live.com/about/en-us/
[Auth0]: https://auth0.com/
[Microsoft Application Registration Portal]: https://apps.dev.microsoft.com
[YAML]: https://en.wikipedia.org/wiki/YAML
[OneDrive APIs]: https://onedrive.live.com/about/en-us/
[`mailgun api key`]: {{ site.baseurl }}/docs/config.html#mailgun api
[`sendgrid api key`]: {{ site.baseurl }}/docs/config.html#sendgrid api
[Google settings]: https://support.google.com/accounts/answer/6010255
[will not be maintained]: https://www.python.org/dev/peps/pep-0373/
[mod_wsgi]: https://modwsgi.readthedocs.io/en/develop/
[mod_php]: https://wiki.apache.org/httpd/php
[mermaid]: https://github.com/mermaidjs/mermaid.cli
[NGINX]: https://www.nginx.com/
[Mailgun API]: {{ site.baseurl }}/docs/config.html#mailgun api
[SendGrid API]: https://sendgrid.com/solutions/email-api/
