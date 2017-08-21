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
integrates nicely with [AWS] services such as [S3] and
[Microsoft Azure] services such as [Azure blob storage] for persistent
storage.

The primary reason you might want to install **docassemble** manually
on a machine is if you want it to run on a server for which the HTTP
and HTTPS ports are serving other applications.  ([Docker] can only
use the HTTP and HTTPS ports if it has exclusive use of them.)

# Supported platforms

The installation instructions in this section assume you are
installing **docassemble** into a 64 bit [Debian]/[Ubuntu] environment
(not using [Docker]).

However, **docassemble** has been developed to be
operating-system-independent.  If you can install the dependencies,
and you know what you're doing, you should be able to get
**docassemble** to run on any operating system, with appropriate
adjustments to the [configuration].  **docassemble** has not been
tested on Mac or Windows, but all the dependencies are likely to be
available for native installation on those platforms.  (E.g., see
[MacTex] for LaTeX on Mac, and [MiKTeX] for LaTeX on Windows.)
However, it would probably take a lot of time to figure this out, any
why bother, when you can install **docassemble** on a Mac or PC using
[Docker]?.

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
needed by those [Python] packages.

For all of the features of **docassemble** to be available, several
other applications need to run concurrently on the same server.  These
applications include:

* A web server (using ports 80 and/or 443);
* A [web sockets] background process (using port 5000);
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
to run, and the **docassemble** application servers need to run
[syslog-ng] background processes that push log file entries to that
central server.

(Installing on [Docker] ensures that all of these additional
applications are running.)

It is highly recommended that you run **docassemble** over HTTPS,
since the web application uses a password system, and because your
users' answers to interview questions may be confidential.  (The
[Docker] startup process can be configured to use [Let's Encrypt] and
to automatically renew the SSL certificates.)

Finally, some of **docassemble**'s features depend on the following
services:

* An [SMTP] server for [sending](#email) (as opposed to receiving)
  e-mails;
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

The following dependencies can be installed from [Debian] or
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
  curl mktemp dnsutils tesseract-ocr tesseract-ocr-dev \
  tesseract-ocr-afr tesseract-ocr-ara tesseract-ocr-aze \
  tesseract-ocr-bel tesseract-ocr-ben tesseract-ocr-bul \
  tesseract-ocr-cat tesseract-ocr-ces tesseract-ocr-chi-sim \
  tesseract-ocr-chi-tra tesseract-ocr-chr tesseract-ocr-dan \
  tesseract-ocr-deu tesseract-ocr-deu-frak tesseract-ocr-ell \
  tesseract-ocr-eng tesseract-ocr-enm tesseract-ocr-epo \
  tesseract-ocr-equ tesseract-ocr-est tesseract-ocr-eus \
  tesseract-ocr-fin tesseract-ocr-fra tesseract-ocr-frk \
  tesseract-ocr-frm tesseract-ocr-glg tesseract-ocr-grc \
  tesseract-ocr-heb tesseract-ocr-hin tesseract-ocr-hrv \
  tesseract-ocr-hun tesseract-ocr-ind tesseract-ocr-isl \
  tesseract-ocr-ita tesseract-ocr-ita-old tesseract-ocr-jpn \
  tesseract-ocr-kan tesseract-ocr-kor tesseract-ocr-lav \
  tesseract-ocr-lit tesseract-ocr-mal tesseract-ocr-mkd \
  tesseract-ocr-mlt tesseract-ocr-msa tesseract-ocr-nld \
  tesseract-ocr-nor tesseract-ocr-osd tesseract-ocr-pol \
  tesseract-ocr-por tesseract-ocr-ron tesseract-ocr-rus \
  tesseract-ocr-slk tesseract-ocr-slk-frak tesseract-ocr-slv \
  tesseract-ocr-spa tesseract-ocr-spa-old tesseract-ocr-sqi \
  tesseract-ocr-srp tesseract-ocr-swa tesseract-ocr-swe \
  tesseract-ocr-tam tesseract-ocr-tel tesseract-ocr-tgl \
  tesseract-ocr-tha tesseract-ocr-tur tesseract-ocr-ukr \
  tesseract-ocr-vie build-essential nodejs npm exim4-daemon-heavy \
  libsvm3 libsvm-dev liblinear1 liblinear-dev libzbar-dev \
  cm-super libgs-dev ghostscript texlive-extra-utils
{% endhighlight %}

The libraries `libcurl4-openssl-dev` and `libssl-dev` are particularly
important; **docassemble**'s [Python] dependencies will not install
unless these libraries are present.

On [Ubuntu], you may need to replace `liblinear1` with `liblinear3`.

**docassemble** depends on a recent version of the [pdfx] package
for [LaTeX].

{% highlight bash %}
wget -O /tmp/pdfx.zip http://mirrors.ctan.org/macros/latex/contrib/pdfx.zip
sudo unzip -o -d /usr/share/texlive/texmf-dist/tex/latex /tmp/pdfx.zip
sudo texhash
rm /tmp/pdfx.zip
{% endhighlight %}

**docassemble** depends on version 5.0.1 or later of the
[Perl Audio Converter] to convert uploaded sound files into other
formats.  If your distribution offers an earlier version, you will
need to install [pacpl] it from the source:

{% highlight bash %}
sudo apt-get -q -y remove pacpl
git clone git://git.code.sf.net/p/pacpl/code pacpl-code 
cd pacpl-code
./configure
make
sudo make install
cd ..
{% endhighlight %}

(Note that these instructions call for the standard [pacpl] to be
installed and then uninstalled; this is a quick way of ensuring that
[pacpl]'s dependencies exist on the system.)

**docassemble** also depends on [Pandoc] version 1.17 or later.  If
your Linux distribution provides an earlier version, you can install
from the source:

{% highlight bash %}
wget https://github.com/jgm/pandoc/releases/download/1.19.2.1/pandoc-1.19.2.1-1-amd64.deb
sudo dpkg -i pandoc-1.19.2.1-1-amd64.deb
{% endhighlight %}

On some systems, you may run into a situation where [LibreOffice]
fails with a "permission denied" error when run by the web server.  To
avoid this, run:

{% highlight bash %}
sudo chmod -R 777 /var/spool/libreoffice
{% endhighlight %}

To enable the use of [Azure blob storage] as a means of
[data storage], you will need to run the following:

{% highlight bash %}
sudo update-alternatives --install /usr/bin/node node /usr/bin/nodejs 10
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
install and upgrade [Python] packages [through the web interface], and
they will not need to use the command line.  Second, installing with
[pip] into a virtual environment will ensure that all of the [Python]
packages are the latest version; the versions that are packaged with
Linux distributions are not always current.

The installation process will require you to be able to run commands
as `www-data`.  By default, your system may prevent the `www-data`
user from using a shell.  Get around this limitation by running the
following:

{% highlight bash %}
sudo chsh -s /bin/bash www-data
sudo chown -R www-data.www-data /var/www
{% endhighlight %}

Before setting up the [Python virtual environment], you need to create
directories needed by [pip] for temporary files and the directories in
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
  /usr/share/docassemble/log \
  /etc/ssl/docassemble
sudo chown -R www-data.www-data /var/www /usr/share/docassemble
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
includes the [SMS] interface), and the
`docassemble.demo` package contains a [demonstration] interview.

<a name="virtualenv"></a>To install **docassemble** and its [Python]
dependencies into the [Python virtual environment], first install the
latest version of [pip], then install the `virtualenv` module:

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
cp ./docassemble/Docker/pip.conf /usr/share/docassemble/local/
source /usr/share/docassemble/local/bin/activate
pip install --upgrade ndg-httpsclient
pip install 'git+https://github.com/nekstrom/pyrtf-ng#egg=pyrtf-ng' \
./docassemble/docassemble \
./docassemble/docassemble_base \
./docassemble/docassemble_demo \
./docassemble/docassemble_webapp
{% endhighlight %}

The `pip.conf` file is necessary because it enables the use of
[GitHub] package references in the `setup.py` files of **docassemble**
extension packages.  The [ndg-httpsclient] module, which is a
dependency, is installed by itself because errors might occur during
installation if this package does not already exist on the system.
There is one [Python] dependency, [PyRTF-ng], which is not available
on [PyPI], but must be installed from [GitHub].  The **docassemble**
packages are installed from the cloned [GitHub] repository.  These
packages are also available on [PyPI], and could be installed with
`pip install docassemble.webapp`, but it is just as easy to install
them from the local copy.

Then, you need to move certain files into place for the web
application.  Still acting as `www-data`, do:

{% highlight bash %}
cp ./docassemble/docassemble_webapp/docassemble.wsgi /usr/share/docassemble/webapp/
cp ./docassemble/Docker/config/* /usr/share/docassemble/config/
cp ./docassemble/Docker/*.sh /usr/share/docassemble/webapp/
cp ./docassemble/Docker/VERSION /usr/share/docassemble/webapp/
{% endhighlight %}

The `docassemble.wsgi` file is the primary "executable" for the web
application.  The web server configuration will point to this file.

The files copied to `/usr/share/docassemble/config/` include configuration
file templates for **docassemble** and [Apache].

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
sudo cp ./docassemble/Docker/docassemble.conf /etc/apache2/conf-available/docassemble.conf
sudo cp ./docassemble/Docker/config/docassemble-http.conf.dist /etc/apache2/sites-available/docassemble-http.conf
sudo cp ./docassemble/Docker/config/docassemble-ssl.conf.dist /etc/apache2/sites-available/docassemble-ssl.conf
sudo cp ./docassemble/Docker/docassemble-supervisor.conf /etc/supervisor/conf.d/docassemble.conf
sudo cp ./docassemble/Docker/ssl/* /usr/share/docassemble/certs/
sudo cp ./docassemble/Docker/rabbitmq.config /etc/rabbitmq/
{% endhighlight %}

The `/etc/apache2/conf-available/docassemble.conf` file contains
instructions for [Apache] to use the virtual environment to run the
**docassemble** web application.  The
`/etc/apache2/sites-available/docassemble-http.conf` and
`/etc/apache2/sites-available/docassemble-ssl.conf` files contain
[Apache] site configuration directives for the **docassemble** web
application.

# Setting up the web application

Enable the [Apache]<span></span> [wsgi], [xsendfile], [rewrite], [proxy], [proxy_http],
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
sudo chown www-data.www-data /usr/share/docassemble/config/config.yml.dist \
  /usr/share/docassemble/webapp/docassemble.wsgi
sudo chown -R www-data.www-data /usr/share/docassemble/local \
  /usr/share/docassemble/log /usr/share/docassemble/files
sudo chmod ogu+r /usr/share/docassemble/config/config.yml.dist
{% endhighlight %}

Then, edit the [Apache] site configuration.

{% highlight bash %}
sudo vi /etc/apache2/sites-available/docassemble-http.conf
{% endhighlight %}

Edit the `ServerAdmin` line and add your e-mail address.

Replace `{% raw %}{{DAHOSTNAME}}{% endraw %}` with the domain of your
site (e.g., `assembly.example.com`).

Replace `{% raw %}{{POSTURLROOT}}{% endraw %}` with `/` and replace
`{% raw %}{{WSGIROOT}}{% endraw %}` with `/`.

However, if you changed the [`root`] directive to `/docassemble/` in
the [configuration], replace `{% raw %}{{POSTURLROOT}}{% endraw %}`
with `/docassemble/` and replace `{% raw %}{{WSGIROOT}}{% endraw %}`
with `/docassemble`.

Make any other changes you need to make so that **docassemble** can
coexist with your other web applications.

If your **docassemble** interviews are not thread-safe, for example
because different interviews on your server use different locales,
change `threads=5` to `processes=5 threads=1`.  This will cause
[Apache] to run [WSGI] in a "prefork" configuration.  This is slower
than the multi-thread configuration.  See [`update_locale()`] for more
information about **docassemble** and thread safety.

Finally, enable the [Apache] configuration files that you installed
earlier.

{% highlight bash %}
sudo a2enconf docassemble
sudo a2ensite docassemble-http
sudo a2ensite docassemble-ssl
{% endhighlight %}

If you did not change the [`root`] directive in the [configuration],
you should make sure the default [Apache] site configuration is
disabled, or else it will conflict with the **docassemble** site
configuration:

{% highlight bash %}
sudo a2dissite 000-default
{% endhighlight %}

If you have your own SSL certificates, you can enable SSL by running:

{% highlight text %}
sudo a2enmod ssl
{% endhighlight %}

You will then need to edit
`/etc/apache2/sites-available/docassemble-ssl.conf` and make the same
changes that you made to
`/etc/apache2/sites-available/docassemble-http.conf`.

Note that the [Apache] configuration file will forward HTTP to HTTPS
if the `ssl` [Apache] module is installed, but will run
**docassemble** solely on HTTP otherwise.

The [Apache] configuration file looks for SSL certificates in
`/etc/ssl/docassemble`.  The best practice is not to edit these file
locations.  Instead, copy your SSL certificates to the following
locations:

* `/usr/share/docassemble/certs/apache.crt` (certificate)
* `/usr/share/docassemble/certs/apache.key` (private key)
* `/usr/share/docassemble/certs/apache.ca.pem` (chain file)

On startup, the [initialization script] will copy these files into
`/etc/ssl/docassemble` with the appropriate ownership and permissions.

If you ran `sudo a2enmod ssl` but wish to go back to using plain HTTP,
run:

{% highlight text %}
sudo a2dismod ssl
{% endhighlight %}

If you do not have your own SSL certificates, it is easy to set up
HTTPS using [Let's Encrypt].  Once you get your site working on HTTP,
you can run a single command line that enables HTTPS on your system.
This is explained [below](#certbot).

# <a name="setup"></a>Setting up the SQL server

`docassemble` uses a SQL database.  This database can be located on
the same server or a different server, but these instructions assume
you are using [PostgreSQL] locally.  Set up the database by running
the following commands.

{% highlight bash %}
echo "create role docassemble with login password 'abc123'; create database docassemble owner docassemble;" | sudo -u postgres psql
sudo -H -u www-data bash -c "source /usr/share/docassemble/local/bin/activate && python -m docassemble.webapp.create_tables"
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
cp ./docassemble/Docker/apache.logrotate /etc/logrotate.d/apache2
cp ./docassemble/Docker/config/docassemble-log.conf.dist /etc/apache2/sites-available/docassemble-log.conf
echo "Listen 8080" >> /etc/apache2/ports.conf
a2enmod cgid
a2ensite docassemble-log
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
  [configuration] to this domain (`help.example.com`).
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

# Connecting to other external services

To obtain the full benefit of **docassemble**, you will need to obtain
IDs and secrets for the web services that **docassemble** uses, which
you supply to **docassemble** by editing the [configuration] file.  In
order for the "Sign in with Google," "Sign in with Facebook," and
"Sign in with Azure" buttons to work, you will need to register your
site on [Google Developers Console], [Facebook Developers], and/or
[Azure Portal].

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

* Log in to [Facebook Developers]
* Add an app.
* Give the app a name.  Users will see this name when they are asked
  to consent to sharing of information between Facebook and your site,
  so be sure to pick a name that your users will recognize.
* Note the App ID that you are assigned.  You need to set
  this value as the `id` in the [`oauth`] configuration, under
  `facebook`.
* Note also the "App Secret."  You need to set this as the `secret` in
  the [`oauth`] configuration.
* Under App Domains, put in the domain of your site.  E.g.,
  `docassemble.example.com`.

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
"GD" button in the [Playground] that, when pressed, will synchronize
the contents of the user's [Playground] with a folder on the user's
[Google Drive].

In order for users to be able to connect their accounts in this way,
you will need to obtain an OAuth 2.0 client ID and secret from
Google.

* Log in to the [Google Developers Console].
* Start a "project" for your server if you do not already have one.
* Enable the [Google Drive API] for the project.
* Under "Credentials," create an OAuth 2.0 client ID for a "web
  application."
* Note the "Client ID."  You need to set this value as the `id` in the
  [`oauth`] configuration, under `googledrive`.
* Note also the "Client secret."  You need to set this as the `secret`
  in the [`oauth`] configuration.
* Under Authorized JavaScript origins, add the URL for your
  **docassemble** site.  (E.g. `https://docassemble.example.com`)
* Under Authorized redirect URIs, add the URL
  `https://docassemble.example.com/google_drive_callback`.

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

In order for users to be able to connect their accounts in this way,
you will need to register your **docassemble** server as an "OAuth
application" on [GitHub]:

* [Create an account on GitHub] if you have not done so already.
* Log in to [GitHub].
* Go to your "[Settings](https://github.com/settings/profile)."
* Navigate to
  "[OAuth applications](https://github.com/settings/developers)."
* Press the "Register a new application" button.
* Enter an "Application name" that describes your **docassemble**
  server.  Your users will see this application name when [GitHub]
  asks them if they wish to grant your server access to their [GitHub]
  account.
* Under "Homepage URL," enter the URL of your **docassemble** server.
* If you want, enter an "Application description."  Users will see
  this when [GitHub] asks them if they wish to grant your server
  access to their [GitHub] account.
* Under "Authorization callback URL," enter the URL for your server
  followed by `/github_oauth_callback`.  So, if your users access the
  [Playground] at `https://docassemble.example.com/playground`, the
  callback URL will be
  `https://docassemble.example.com/github_oauth_callback`.  This
  setting needs to be precisely set or else the integration will not
  work.
* Press the "Register application" button.
* [GitHub] will then tell you the "Client ID" and "Client Secret" of
  your new "OAuth application."  Note the values of these codes; you
  need to plug them into your **docassemble** [configuration].
* On your **docassemble** server, go to "Configuration."  Set the
  "Client ID" value as the `id` in the [`oauth`] configuration, under
  `github`.  Set the "Client Secret" value as the `secret` in the
  [`oauth`] configuration.

The server will restart after you change the [configuration].  Then,
when you go to your "Profile," you should see a "GitHub integration"
link.

When users click this link and they choose to associate their [GitHub]
account with their account on your **docassemble** server,
**docassemble** stores an access token in [Redis] for the user.  This
allows **docassemble** to authenticate with the [GitHub API].
**docassemble** also creates an SSH private key and an SSH public key
annotated with the e-mail address associated with the user's [GitHub]
account.  These SSH keys are stored in the same directory in the
Playground as the files for [Playground] packages, so they will appear
in [Google Drive] if [Google Drive synchronization] is enabled, and
they will be stored in the cloud if cloud [data storage] is enabled.
Using the [GitHub API], **docassemble** stores the public key in the
user's [GitHub] account, using the name of the application as
specified in the [configuration] as the value of [`appname`] (which
defaults to `docassemble`).

## <a name="email"></a>Setting up e-mail sending

If you plan to use the [roles] feature or the [`send_email()`]
function, you will need an [SMTP] server.

While it is easy to deploy an [SMTP] server, most cloud providers
block outgoing [SMTP] connections.  As a result, you may have to use a
special service to send e-mail, such as [Amazon SES], [SendGrid]
(which is particularly easy to set up if you host on
[Microsoft Azure]), [MailChimp], [Mailgun], and [Google Apps].  To set
up e-mail sending, see the [`mail`] directive in the [configuration].

If you have a Google account, you can use a Gmail [SMTP] server by
setting the following in your [configuration]:

{% highlight yaml %}
mail:
  server: smtp.gmail.com
  username: yourgoogleusername
  password: yourgooglepassword
  use_ssl: True
  port: 465
  default_sender: '"Administrator" <no-reply@example.com>'
{% endhighlight %}

Note that for this to work, you will need to go into your Google
settings and set "Allow less secure apps" to "ON."

You can also use the [Amazon SES] service to send e-mail.  When you
set it up, you will be given a username, password, and server.  In the
**docassemble** configuration, you would write something like this:

{% highlight yaml %}
mail:
  username: WJYAKIBAJVIFYAETTC3G
  password: At6Cz2BH8Tx1zqPp0j3XhzlhbRnYsmBx7WwoItL9N5GU
  server: email-smtp.us-east-1.amazonaws.com
  default_sender: '"Example Inc." <no-reply@example.com>'
{% endhighlight %}

In order to send e-mail through [Amazon SES], you will need to verify
your domain.  Among other things, this involves editing your [DNS]
configuration to add a [TXT record] for the host `_amazonses`.

To ensure that e-mails from your application are not blocked by spam
filters, you should also add a [TXT record] with [SPF] information for
your domain, indicating that [Amazon SES] is authorized to send e-mail
for your domain:

{% highlight text %}
v=spf1 mx include:amazonses.com ~all
{% endhighlight %}

Initially, [Amazon SES] puts your account in a "sandbox" that allows
you to send e-mails only to addresses you manually verify.  To get out
of this "sandbox," you need to [submit a support request] describing
your use case and your policies for dealing with reply e-mails.

Instead of using [Amazon SES], you could use a third party mail
service like [SendGrid], [Mailgun], or [MailChimp].  Note that in order
to minimize the chances that e-mail you send from these services will
be flagged as spam, you will need to spend some time configuring
[SPF] records, [DKIM] records, [reverse DNS], and the like.  It is also
possible to use an [SMTP] server from [Google Apps] if you have a
[G Suite] account.

# Start the server and background processes

First, we need to disable the automatic starting and stopping of
[Apache] on your server.  Your server will still run [Apache], but we
need it to be controlled by [supervisor] rather than [systemd]:

{% highlight bash %}
sudo systemctl stop apache2.service
sudo systemctl disable apache2.service
{% endhighlight %}

If you are using the [e-mail receiving] feature, disable the exim4
service as well:
{% highlight bash %}
sudo systemctl stop exim4.service
sudo systemctl disable exim4.service
{% endhighlight %}

Make sure that [Redis] and [RabbitMQ] are already running.  They
should have started running after installation.

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

While [RabbitMQ] should have been started after you installed it, you
still need to restart it because you gave it a new configuration file,
which it has not processed yet:

{% highlight bash %}
sudo systemctl restart rabbitmq-server.service
{% endhighlight %}

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

Finally, restart the [supervisor] service:

{% highlight bash %}
sudo systemctl stop supervisor.service
sudo systemctl start supervisor.service
{% endhighlight %}

You should find **docassemble** running at the URL for your site.

<a name="certbot"></a>If you did not enable HTTPS in your [Apache]
configuration, an easy way to encrypt your site is through
[Let's Encrypt], also known as [certbot].  To install the software,
follow the [certbot instructions] for your operating system.  For
example, on Ubuntu 16.04, you can add the latest [certbot] to your
software repository by doing:

{% highlight bash %}
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
{% endhighlight %}

Then, to install [certbot], run:

{% highlight bash %}
sudo apt-get -y update
sudo apt-get -y install python-certbot-apache 
{% endhighlight %}

Once [certbot] is installed, you can change your site from HTTP to
HTTPS by running:

{% highlight bash %}
sudo certbot --apache
{% endhighlight %}

When it asks you to "choose whether HTTPS access is required or
optional," select option 2, "Secure - Make all requests redirect to
secure HTTPS access."

Once your site is using HTTPS, you should change the password for the
default admin user.  Click "Sign in or sign up to save
answers" or navigate to `/user/sign-in`.  Log in with:

* Email: admin@admin.com
* Password: password

It should immediately prompt you to change your password to something secure.

# Debugging

Run `sudo supervisorctl status` to see the status of the processes `supervisor` is
controlling.  A healthy output would look like this:

{% highlight text %}
apache2                          RUNNING   pid 1894, uptime 0:08:49
celery                           RUNNING   pid 2592, uptime 0:00:11
cron                             STOPPED   Not started
exim4                            RUNNING   pid 2198, uptime 0:04:07
initialize                       RUNNING   pid 1111, uptime 0:09:17
postgres                         STOPPED   Not started
rabbitmq                         STOPPED   Not started
redis                            STOPPED   Not started
reset                            STOPPED   Not started
sync                             EXITED    May 28 07:52 PM
syslogng                         STOPPED   Not started
update                           STOPPED   Not started
watchdog                         RUNNING   pid 1110, uptime 0:09:17
websockets                       RUNNING   pid 1589, uptime 0:09:05
{% endhighlight %}

The `postgres`, `rabbitmq`, and `redis` services are not being
controlled by [supervisor] in this example, but they should be
running.

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
* `/var/log/apache2/error.log`
* `/usr/share/docassemble/log/docassemble.log`
* `/tmp/flask.log`

If the `celery` process failed to start, or you are debugging
[background processes], check:

* `/usr/share/docassemble/log/worker.log`

If you are debugging [e-mail receiving], check:

* `/tmp/mail.log`
* `/var/log/exim4/mainlog`

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

If you need to run [Python] commands like [pip] in order to fix
problems, you need to run `su www-data` so that you are running as the
same user as [Apache].  In addition, you need to let the shell know
about the virtual environment.  You can do this by running the
following before you run any [Python] commands:

{% highlight bash %}
source /usr/share/docassemble/local/bin/activate
{% endhighlight %}

If you encounter any errors, please register an "issue" on the
**docassemble** [issues page]({{ site.github.repository_url }}/issues).

# Using different web servers and/or SQL database backends

**docassemble** needs a web server and a SQL server, but it is not
  dependent on [Apache] or [PostgreSQL].

Other web servers that can host Python [WSGI] applications (e.g.,
[nginx] with [uWSGI]) could be used.

**docassemble** uses [SQLAlchemy] to communicate with the SQL back
end, so you can edit the [configuration] to point to another type of
database system, if supported by [SQLAlchemy].  **docassemble** does
not do fancy things with SQL, so most backends should work without a
problem.  Any backend that you use must support column definitions
with `server_default=db.func.now()`.

One reason you might want to stay with [PostgreSQL], however, is that
**docassemble** has utilities for automatically updating database
columns if a new version of **docassemble** requires changes to
columns in existing database tables.  If you use a non-[PostgreSQL]
database, you will need to make these changes manually.

# Running services on different machines

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
cp ./Docker/VERSION /usr/share/docassemble/webapp/
python -m docassemble.webapp.fix_postgresql_tables
python -m docassemble.webapp.create_tables
exit
{% endhighlight %}

If you get any errors while upgrading with [pip], try doing the
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
[proxy_wstunnel]: https://httpd.apache.org/docs/current/mod/mod_proxy_wstunnel.html
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[nginx]: https://www.nginx.com/
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
[OAuth2]: https://oauth.net/2/
[`oauth`]: {{ site.baseurl }}/docs/config.html#oauth
[LibreOffice]: https://www.libreoffice.org/
[certbot instructions]: https://certbot.eff.org/all-instructions/
[certbot]: https://certbot.eff.org/
[Google Drive synchronization]: {{ site.baseurl }}/docs/playground.html#google drive
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
[Google Drive]: https://drive.google.com
[Google Drive API]: https://developers.google.com/drive/v3/web/about-sdk
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
