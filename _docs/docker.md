---
layout: docs
title: Installing on Docker
short_title: Docker
---

[Docker] is a good platform for trying out **docassemble** for the
first time.  It can also be used as a production environment; Amazon's
[EC2 Container Service] can be used to maintain a cluster of
**docassemble** web server instances, created from [Docker] images,
that communicate with a central SQL server.  For information about how
to install **docassemble** in a multi-server arrangement on
[EC2 Container Service] ("[ECS]"), see the [scalability] section.

# Prerequisites

Make sure you have at least 12GB of storage space.  (**docassemble**
has a lot of large dependencies.)  At the end of installation, only
about 4GB will be taken up, but the build and installation processes
require more storage than that to be available.

# Installing Docker

If you have a Mac, follow the [Docker installation instructions for OS X]{:target="_blank"}.

If you have a Windows PC, follow the [Docker installation instructions for Windows]{:target="_blank"}.

On [Amazon Linux] (assuming the username `ec2-user`):

{% highlight bash %}
sudo yum -y update
sudo yum -y install docker
sudo usermod -a -G docker ec2-user
{% endhighlight %}

On Ubuntu (assuming username `ubuntu`):

{% highlight bash %}
sudo apt-get -y update
sudo apt-get -y install docker.io
sudo usermod -a -G docker ubuntu
{% endhighlight %}

The last line allows the non-root user to run [Docker].  You may need to
log out and log back in again for the new user permission to take
effect.

To start [Docker], do:

{% highlight bash %}
sudo /etc/init.d/docker start
{% endhighlight %}

or, on systemd,

{% highlight bash %}
systemctl start docker
{% endhighlight %}

or, on upstart,

{% highlight bash %}
service docker start
{% endhighlight %}

# <a name="single server arrangement"></a>Single-server arrangement

**docassemble** is [available on Docker Hub].  You can download and
run the image by doing:

{% highlight bash %}
docker run -d -p 80:80 -p 443:443 -p 9001:9001 jhpyle/docassemble
{% endhighlight %}

Or, if you are already using port 80 on your machine, use something
like `-p 8080:80` instead.

The image, which is about 2.4GB in size, is an [automated build] based
on the "master" branch of the [docassemble repository].

You can then connect to the container by pointing your web browser to
the IP address or hostname of the machine that is running [Docker].
You can log in using the default username ("admin@admin.com") and
password ("password"), and make changes to the configuration from the
menu.

You should not need to connect to the running container in order to
get it to work.  However, you might want to gain access to the running
container for some reason.  To do so, you can run:

{% highlight bash %}
docker exec -t -i <containerid> /bin/bash
{% endhighlight %}

You can find out the ID of the running container by doing `docker ps`.

Log files you might wish to check include:

* `/var/log/supervisor/initialize-stderr---supervisor-*.log`
* `/var/log/supervisor/postgres-stderr---supervisor-*.log`
* `/var/log/apache2/error.log`
* `/usr/share/docassemble/log/docassemble.log`

Make sure to cleanly shut down the container by running:

{% highlight bash %}
docker stop -t 60 <containerid>
{% endhighlight %}

The container runs a [PostgreSQL] server, and the data files of the
server may become corrupted if [PostgreSQL] is not gracefully shut down.

By default, [Docker] gives containers ten seconds to shut down before
forcibly shutting them down, but sometimes [PostgreSQL] takes a little
longer than ten seconds, so it is a good idea to give the container
plenty of time to shut down gracefully.  The `-t 60` means that [Docker]
will wait up to 60 seconds before forcibly shutting down the
container.  Usually the container will shut down in about ten seconds.

To see a list of stopped containers, run `docker ps -a`.  To remove a
container, run `docker rm <containerid>`.

## Configuration options

The **docassemble** [Docker] installation is configurable with
environment variables.  From the [Docker] command line, these variables
can be included with the `--env-file=env.list` option, where
`env.list` is a text file containing variable definitions in standard
shell script format.  When running **docassemble** in [ECS], these
variables are specified in [JSON] text that is provided through the
web interface.  (See the [scalability] section for more information
about [ECS].)

Here is a sample `env.list` file:

{% highlight text %}
DAHOSTNAME=legalhelp.com
LOCALE=en_US.UTF-8 UTF-8
TIMEZONE=America/New_York
USEHTTPS=true
USELETSENCRYPT=true
LETSENCRYPTEMAIL=admin@legalhelp.com
{% endhighlight %}

This will cause the [Apache] configuration file to use legalhelp.com as
the `ServerName`.  The `LOCALE` is appended to `/etc/locale.gen` and
`locale-gen` and `update-locale` are run.  The `TIMEZONE` is stored in
`/etc/timezone` and `dpkg-reconfigure -f noninteractive tzdata` is run.

The available environment variables include:

* `CONTAINERROLE`: options are:
  * `all`: the [Docker] container will serve as the [PostgreSQL] server as
    well as the sole application server.
  * `webserver`: The [Docker] container will not start a [PostgreSQL]
    server, but will use the database specified in the `DBHOST` variable.
* `DBHOST`: The hostname of the [PostgreSQL] server.  Keep undefined
  or set to `null` in order to use the [PostgreSQL] server on the same
  host.  This environment variable, along with others that begin with
  `DB`, populates values in [db] section of the [configuration] file.
* `DBNAME`: The name of the [PostgreSQL] database.  Default is `docassemble`.
* `DBUSER`: The username for connecting to the [PostgreSQL] server.
  Default is `null` because the default is for **docassemble** to
  connect to the database using "peer" authentication using the role
  `www-data` (which is the username of the [Apache] process).
* `DBPASSWORD`: The password for connecting to the SQL server.
  Default is `null`.
* `DBPREFIX`: This sets the prefix for the database specifier.  The
  default is `postgresql+psycopg2://`.
* `DBPORT`: This sets the port that **docassemble** will use to access
  the SQL server.
* `DBTABLEPREFIX`: This allows multiple separate **docassemble**
  implementations to share the same SQL database.  The value is a
  prefix to be added to each table in the database.
* `EC2`: Set this to `true` if you are running [Docker] on [EC2].
  This allows **docassemble** to determine the hostname of the server
  on which it is running.  This populates the [ec2] setting in the
  [configuration].
* `USEHTTPS`: Set this to `true` if you would like **docassemble** to
  communicate with the browser using encryption.  See [HTTPS] for more
  information.  Defaults to `false`.
* `DAHOSTNAME`: Set this to the hostname by which web browsers can find
  **docassemble**.  This is necessary for [HTTPS] to function.
* `USELETSENCRYPT`: Set this to `true` if you are
  [using Let's Encrypt].  The default is `false`.
* `LETSENCRYPTEMAIL`: Set this to the e-mail address you use with
  [Let's Encrypt].
* `LOCALE`: You can use this to enable a locale on the server.  When
  the server starts, the value of `LOCALE` is appended to
  `/etc/locale.gen` and `locale-gen` and `update-locale` are run.
* `LOGSERVER`: This is used in the [multi-server arrangement] where
  there is a separate server for collecting log messages.  The default
  is `none`, which causes the server to run [Syslog-ng].
* `S3ENABLE`: Set this to `true` if you are using [S3] as a repository
  for uploaded files, [Playground] files, and the [configuration]
  file.  This environment variable, along with others that begin with
  `S3`, populates values in [s3] section of the [configuration] file.
* `S3ACCESSKEY`: If you are using [S3], set this to the [S3] access key.
* `S3SECRETACCESSKEY`: If you are using [S3], set this to the [S3]
  access secret.
* `S3BUCKET`: If you are using [S3], set this to the bucket name.
  Note that **docassemble** will not create the bucket for you.  You
  will need to create it for yourself beforehand.
* `TIMEZONE`: You can use this to set the time zone of the server.
  The value of the variable is stored in `/etc/timezone` and
  `dpkg-reconfigure -f noninteractive tzdata` is run in order to set
  the system time zone.

Note that if you use [persistent volumes] and/or [S3], launching a new
**docassemble** container with different variables is not necessarily
going to change the way **docassemble** works.  For example:

* If `HTTPS` is `true` and `USELETSENCRYPT` is `true`, then the
  [Apache] configuration files, if stored on a persistent volume, will
  not be overwritten if they already exist when a new container starts
  up.  So if you are using [Let's Encrypt] and you want to change the
  `DAHOSTNAME`, run `docker volume rm letsencrypt` to remove the
  [Let's Encrypt] configuration before running a new container.
* If `S3ENABLE` is `true`, then on startup, the container will
  retrieve the configuration file from [S3] and use it as the
  configuration of **docassemble**, all before the web server even
  starts.  Therefore, if you are using [S3], the environment variables
  to set the database configuration ([db]) will have no effect.  To
  edit the database access information, edit the configuration file
  that exists on [S3].

## <a name="persistent"></a>Using persistent volumes

To run **docassemble** in a [single-server arrangement] in such a way
that the [configuration], the [Playground] files, and the uploaded
files persist after the [Docker] container is removed or updated, run
the image as follows:

{% highlight bash %}
docker run --env-file=env.list \
-v pgetc:/etc/postgresql \
-v pglog:/var/log/postgresql \
-v pglib:/var/lib/postgresql \
-v pgrun:/var/run/postgresql \
-v dalog:/usr/share/docassemble/log \
-v dafiles:/usr/share/docassemble/files \
-v certs:/usr/share/docassemble/certs \
-v daconfig:/usr/share/docassemble/config \
-v dabackup:/usr/share/docassemble/backup \
-v letsencrypt:/etc/letsencrypt \
-v apache:/etc/apache2/sites-available \
-d -p 80:80 -p 443:443 jhpyle/docassemble
{% endhighlight %}

where `--env-file=env.list` is an optional parameter that refers to a
file `env.list` containing environment variables for the
configuration.

To delete all of the volumes, do:

{% highlight bash %}
docker volume rm $(docker volume ls -qf dangling=true)
{% endhighlight %}

An advantage of using persistent volumes is that you can completely
replace the **docassemble** container and rebuild it from scratch, and
when you `run` the `jhpyle/docassemble` image again, docassemble will
keep running where it left off.  This also facilitates backing up a
**docassemble** server that runs on Docker.  For example, here is a
script that backs up the **docassemble** implementation running on a
remote server, `dev.docassemble.org`:

{% highlight bash %}
rsync -au --rsync-path="sudo rsync" dev.docassemble.org:/var/lib/docker/volumes /root/my-backup-directory
{% endhighlight %}

Note: for this to run unattended, you need to edit `~/.ssh/config` to
indicate where the identity file is located:

{% highlight text %}
Host dev.docassemble.org
    HostName dev.docassemble.org
    User ec2-user
    IdentityFile /root/ec2-user.pem
{% endhighlight %}

## Cleaning up after multiple builds

If you build docker images, you may find your disk space being used
up.  These three lines will stop all containers, remove all
containers, and then remove all of the images that [Docker] created
during the build process.

{% highlight bash %}
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images | grep "^<none>" | awk "{print $3}")
{% endhighlight %}

# Multi-server arrangement

To run **docassemble** in a [multi-server arrangement] using [Docker],
you need to:

1. Start a container that will provide the SQL server;
2. Start a container that will provide the log server;
3. Start one or more other containers that will handle the
**docassemble** application and web server.

These containers can be on separate hosts.

The containers need to have a way to share files with one another.
The best way to do this is with [Amazon S3].  Before proceeding, go to
[Amazon S3] and obtain an access key and a secret access key.  Then
create a bucket and remember the name of the bucket.

First, go to the machine that will host the SQL server.  To start the
SQL server, do:

{% highlight bash %}
docker run -d -p 5432:5432 jhpyle/docassemble-sql
{% endhighlight %}

Note the IP address or hostname of the [Docker] host on the local
network.  You will need to feed this address, and other information,
to the [Docker] container that responds to web requests.

Now go to the machine that will run your log server (if different).
To start the log server, do:

{% highlight bash %}
docker run -d -p 514:514 -p 8080:80 jhpyle/docassemble-log
{% endhighlight %}

Note the IP address or hostname of this server as well.

Now go to the machine that will run your application server (if different).

Plug the IP addresses or hostnames for the SQL server and log server
into a file called `env.list`, along with your [S3] information:

{% highlight text %}
CONTAINERROLE=webserver
DBNAME=docassemble
DBUSER=docassemble
DBPASSWORD=abc123
DBHOST=192.168.0.56
USEHTTPS=false
DAHOSTNAME=host.example.com
USELETSENCRYPT=false
LETSENCRYPTEMAIL=admin@admin.com
S3ENABLE=true
S3ACCESSKEY=FWIEJFIJIDGISEJFWOEF
S3SECRETACCESSKEY=RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
S3BUCKET=yourbucketname
EC2=false
TIMEZONE=America/New_York
LOGSERVER=192.168.0.57
{% endhighlight %}

The address for the SQL server is `DBHOST`.  The address for the log
server is `LOGSERVER`.

Then start the application server:

{% highlight bash %}
docker run --env-file=env.list -d -p 80:80 -p 443:443 -p 9001:9001 jhpyle/docassemble
{% endhighlight %}

You can start multiple application servers in this way.

Port 9001 is opened so that application servers can coordinate with
one another.  For example, if one of the servers updates the
configuration, it can send a message to all of the other servers,
instructing them to retrieve the new configuration.

See [scalability of docassemble] for more information about running
**docassemble** in a multi-server arrangement.

# <a name="https"></a>Using HTTPS

## <a name="letsencrypt"></a>With Let's Encrypt

Note: using [Let's Encrypt] to enable [HTTPS] only works in a
[single-server arrangement].

In your task definition or `env.list` file, set the following
environment variables:

* `USELETSENCRYPT`: set this to `true`.
* `LETSENCRYPTEMAIL`: [Let's Encrypt] requires an e-mail address, which
  it will use to get in touch with you about renewing the SSL certificates.
* `DAHOSTNAME`: set this to the hostname that users will use to get to
  the web application.  [Let's Encrypt] needs this in order to verify
  that you have access to the host.
* `USEHTTPS`: set this to `true`.

For example, your `env.list` may look like:

{% highlight text %}
CONTAINERROLE=all
DBNAME=docassemble
USEHTTPS=true
DAHOSTNAME=host.example.com
USELETSENCRYPT=true
LETSENCRYPTEMAIL=admin@admin.com
TIMEZONE=America/New_York
{% endhighlight %}

The first time the server is started, the `letsencrypt` utility will
be run, which will change the [Apache] configuration in order to use the
appropriate SSL certificates.  When the server is later restarted,
the `letsencrypt renew` command will be run, which will refresh the
certificates if they are within 30 days of expiring.

In addition, a script will run on a weekly basis to attempt to renew
the certificates.

## Without Let's Encrypt

See [using HTTPS] for instructions on setting up HTTPS without using
[Let's Encrypt].

Using your own SSL certificates with [Docker] requires that your SSL
certificates reside within each container.  There are three ways to
accomplish this:

* Use [S3], as explained in the [using HTTPS] section.
* Use [persistent volumes] and copy the SSL certificate files
  (`docassemble.key`, `docassemble.crt`, and `docassemble.ca.pem`)
  into the volume for `/usr/share/docassemble/certs` before starting
  the container.
* [Build your own private image] in which your SSL certificates are
  placed in `Docker/docassemble.key`, `Docker/docassemble.crt`, and
  `Docker/docassemble.ca.pem`.  During the build process, these files
  will be copied into `/usr/share/docassemble/certs`.

# <a name="build"></a>Creating your own Docker image

To create your own [Docker] image, first make sure git is installed:

{% highlight bash %}
sudo apt-get -y install git
{% endhighlight %}

or

{% highlight bash %}
sudo yum -y install git
{% endhighlight %}

Then download docassemble:

{% highlight bash %}
git clone {{ site.github.repository_url }}
{% endhighlight %}

To make changes to the configuration of the **docassemble**
application that will be installed in the image, edit the following
files:

* <span></span>[`docassemble/Dockerfile`]: you may want to change the locale and the
  Debian mirror; the standard "httpredir" mirror can lead to random
  packages not being downloaded, depending on which mirrors it chooses
  to use.
* <span></span>[`docassemble/Docker/config.yml`]: you probably do not need to change
  this; it is a template that is updated based on the contents of the
  `--env-file` passed to [`docker run`].  Once your server is up and
  running you can change the rest of the configuration in the web
  application.
* <span></span>[`docassemble/Docker/initialize.sh`]: this script updates `config.yml`
  based on the environment variables; retrieves a new version of
  `config.yml` from [S3], if available; if `CONTAINERROLE` is not set
  to `webserver`, starts the [PostgreSQL] server and initializes the
  database if it does not exist; creates the tables in the database if
  they do not already exist; copies SSL certificates from [S3] or
  `/usr/share/docassemble/certs` if [S3] is enabled; enables the
  [Apache] `mod_ssl` if `USEHTTPS` is `true` and otherwise disables it;
  runs the Let's Encrypt utility if `USELETSENCRYPT` is `true` and the
  utility has not been run yet; and starts [Apache].
* <span></span>[`docassemble/Docker/apache.conf`]: note that if `mod_ssl` is enabled,
  HTTP will merely redirect to HTTPS.
* <span></span>[`docassemble/Docker/docassemble.crt`]: SSL certificate for HTTPS.
* <span></span>[`docassemble/Docker/docassemble.key`]: SSL certificate for HTTPS.
* <span></span>[`docassemble/Docker/docassemble.ca.pem`]: SSL certificate for HTTPS.
* <span></span>[`docassemble/Docker/docassemble.conf`]: [Apache] configuration file
  that causes [Apache] to use the [Python virtualenv].
* <span></span>[`docassemble/Docker/docassemble-supervisor.conf`]: [supervisor]
  configuration file.
* <span></span>[`docassemble/Docker/docassemble.wsgi`]: WSGI server file called by
  [Apache].
* <span></span>[`docassemble/Docker/docassemble.logrotate`]: This file will be copied
  into `/etc/logrotate.d` and will control the rotation of the
  **docassemble** log file in `/usr/share/docassemble/log`.
* <span></span>[`docassemble/Docker/apache.logrotate`]: This replaces the standard
  apache logrotate configuration.  It does not compress old log files,
  so that it is easier to view them in the web application.
* <span></span>[`docassemble/Docker/run-postgresql.sh`]: This is a script that is
  run by [supervisor] to start the [PostgreSQL] server in a
  single-server configuration.
* <span></span>[`docassemble/Docker/docassemble-syslogng.conf`]: The configuration
  for sending [Apache] and supervisor logs to the central log server.

To build the image, run:

{% highlight bash %}
cd docassemble
docker build -t yourdockerhubusername/mydocassemble .
{% endhighlight %}

You can then run your image:

{% highlight bash %}
docker run -d -p 80:80 -p 443:443 -p 9001:9001 yourdockerhubusername/mydocassemble
{% endhighlight %}

Or push it to [Docker Hub]:

{% highlight bash %}
docker push yourdockerhubusername/mydocassemble
{% endhighlight %}

# Upgrading a docker image

As new versions of **docassemble** become available, you can obtain
the latest version by running:

{% highlight bash %}
docker pull jhpyle/docassemble
{% endhighlight %}

Then, subsequent commands will use the latest **docassemble** image.

[Docker installation instructions for Windows]: https://docs.docker.com/engine/installation/windows/
[Docker installation instructions for OS X]: https://docs.docker.com/engine/installation/mac/
[Docker]: https://www.docker.com/
[Amazon AWS]: http://aws.amazon.com
[automated build]: https://docs.docker.com/docker-hub/builds/
[scalability of docassemble]: {{ site.baseurl }}/docs/scalability.html
[Amazon Linux]: https://aws.amazon.com/amazon-linux-ami/
[EC2]: https://aws.amazon.com/ec2/
[single-server arrangement]: #single server arrangement
[multi-server arrangement]: {{ site.baseurl }}/docs/scalability.html
[EC2 Container Service]: https://aws.amazon.com/ecs/
[S3]: https://aws.amazon.com/s3/
[supervisor]: http://supervisord.org/
[available on Docker Hub]: https://hub.docker.com/r/jhpyle/docassemble/
[Docker Hub]: https://hub.docker.com/
[scalability]: {{ site.baseurl }}/docs/scalability.html
[Amazon S3]: https://aws.amazon.com/s3/
[using HTTPS]: {{ site.baseurl }}/docs/scalability.html#ssl
[docassemble repository]: {{ site.github.repository_url }}
[`docassemble/Dockerfile`]: {{ site.github.repository_url }}/blob/master/Dockerfile
[`docassemble/Docker/config.yml`]: {{ site.github.repository_url }}/blob/master/Docker/config.yml
[`docassemble/Docker/initialize.sh`]: {{ site.github.repository_url }}/blob/master/Docker/initialize.sh
[`docassemble/Docker/apache.conf`]: {{ site.github.repository_url }}/blob/master/Docker/apache.conf
[`docassemble/Docker/docassemble.crt`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.crt
[`docassemble/Docker/docassemble.key`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.key
[`docassemble/Docker/docassemble.ca.pem`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.ca.pem
[`docassemble/Docker/docassemble.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.conf
[`docassemble/Docker/docassemble-supervisor.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble-supervisor.conf
[`docassemble/Docker/docassemble.wsgi`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.wsgi
[`docassemble/Docker/docassemble.logrotate`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.logrotate
[`docassemble/Docker/apache.logrotate`]: {{ site.github.repository_url }}/blob/master/Docker/apache.logrotate
[`docassemble/Docker/run-postgresql.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-postgresql.sh
[`docassemble/Docker/docassemble-syslogng.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble-syslogng.conf
[`docker run`]: https://docs.docker.com/engine/reference/run/
[ECS]: https://aws.amazon.com/ecs/
[JSON]: https://en.wikipedia.org/wiki/JSON
[PostgreSQL]: http://www.postgresql.org/
[HTTPS]: #https
[Let's Encrypt]: https://letsencrypt.org/
[using Let's Encrypt]: #letsencrypt
[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[Python virtualenv]: {{ site.baseurl }}/docs/installation.html#virtualenv
[Playground]: {{ site.baseurl }}/docs/playground.html
[Syslog-ng]: https://en.wikipedia.org/wiki/Syslog-ng
[persistent volumes]: #persistent
[configuration]: {{ site.baseurl }}/docs/config.html
[db]: {{ site.baseurl }}/docs/config.html#db
[s3]: {{ site.baseurl }}/docs/config.html#s3
[ec2]: {{ site.baseurl }}/docs/config.html#ec2
[Build your own private image]: #build
