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
[EC2 Container Service], see the [scalability] section.

# Prerequisites

Make sure you have at least 12GB of storage space.  (**docassemble**
has a lot of large dependencies.)  At the end of installation, only
about 4GB will be taken up, but the build and installation processes
require more storage than that to be available.

# Installing Docker

If you have a Mac, follow the [Docker installation instructions for OS X]{:target="_blank"}.

If you have a Windows PC, follow the [Docker installation instructions for Windows]{:target="_blank"}.

On [Amazon Linux] (assuming the username ec2-user):

{% highlight bash %}
sudo yum -y update
sudo yum -y install docker
sudo usermod -a -G docker ec2-user
{% endhighlight %}

On Ubuntu (assuming username ubuntu):

{% highlight bash %}
sudo apt-get -y update
sudo apt-get -y install docker.io
sudo usermod -a -G docker ubuntu
{% endhighlight %}

The last line allows the non-root user to run [Docker].  You may need to
log out and log back in again for the new user permission to take
effect.

To start Docker, do:

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

# Single-server arrangement

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

The container runs a PostgreSQL server, and the data files of the
server may become corrupted if PostgreSQL is not gracefully shut down.

By default, Docker gives containers ten seconds to shut down before
forcibly shutting them down, but sometimes PostgreSQL takes a little
longer than ten seconds, so it is a good idea to give the container
plenty of time to shut down gracefully.  The `-t 60` means that Docker
will wait up to 60 seconds before forcibly shutting down the
container.  Usually the container will shut down in about ten seconds.

To see a list of stopped containers, run `docker ps -a`.  To remove a
container, run `docker rm <containerid>`.

## Using persistent volumes

To run **docassemble** in a single-server arrangement in such a way
that the configuration persists after the Docker container is removed
or updated, run it as follows:

{% highlight bash %}
docker run --env-file=env.list \
-v pgetc:/etc/postgresql \
-v pglog:/var/log/postgresql \
-v pglib:/var/lib/postgresql \
-v pgrun:/var/run/postgresql \
-v dalog:/usr/share/docassemble/log \
-v dafiles:/usr/share/docassemble/files \
-v daconfig:/usr/share/docassemble/config \
-v dabackup:/usr/share/docassemble/backup \
-v letsencrypt:/etc/letsencrypt \
-v apache:/etc/apache2/sites-available \
-d -p 80:80 -p 443:443 -p 9001:9001 jhpyle/docassemble
{% endhighlight %}

where `--env-file=env.list` is an optional parameter that refers to a
file `env.list` containing environment variables for the
configuration.  (More on that below.)

An advantage of using persistent containers is that you can completely
replace the docassemble container and rebuild it from scratch, and
when you `run` the `jhpyle/docassemble` image again, docassemble will
keep running where it left off.  This also facilitates backup

To delete all of the volumes, do:

{% highlight bash %}
docker volume rm $(docker volume ls -qf dangling=true)
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

To start the SQL server, do:

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
HOSTNAME=host.example.com
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

See [scalability of docassemble] for more information about running
**docassemble** in a multi-server arrangement.

# Using HTTPS

### With Let's Encrypt

Note: using Let's Encrypt to enable HTTPS only works in a
single-server arrangement.

In your task definition or `env.list` file, set the following
environment variables:

* `USELETSENCRYPT`: set this to `true`.
* `LETSENCRYPTEMAIL`: Let's Encrypt requires an e-mail address, which
  it will use to get in touch with you about renewing the SSL certificates.
* `HOSTNAME`: set this to the hostname that users will use to get to
  the web application.  Let's Encrypt needs this in order to verify
  that you have access to the host.
* `USEHTTPS`: set this to `true`.

For example, your `env.list` may look like:

{% highlight text %}
CONTAINERROLE=all
DBNAME=docassemble
USEHTTPS=true
HOSTNAME=host.example.com
USELETSENCRYPT=true
LETSENCRYPTEMAIL=admin@admin.com
TIMEZONE=America/New_York
{% endhighlight %}

The first time the server is started, the `letsencrypt` utility will
be run, which will change the Apache configuration in order to use the
appropriate SSL certificates.  When the server is later restarted,
the `letsencrypt renew` command will be run, which will refresh the
certificates if they are within 30 days of expiring.

In addition, a script will run on a weekly basis to attempt to renew
the certificates.

### Without Let's Encrypt

See [using HTTPS] for instructions on setting up HTTPS without using
Let's Encrypt.

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
  to `webserver`, starts the PostgreSQL server and initializes the
  database if it does not exist; creates the tables in the database if
  they do not already exist; copies SSL certificates from [S3] or
  `/usr/share/docassemble/certs` if [S3] is enabled; enables the
  Apache `mod_ssl` if `USEHTTPS` is `true` and otherwise disables it;
  runs the Let's Encrypt utility if `USELETSENCRYPT` is `true` and the
  utility has not been run yet; and starts Apache.
* <span></span>[`docassemble/Docker/apache.conf`]: note that if `mod_ssl` is enabled,
  HTTP will merely redirect to HTTPS.
* <span></span>[`docassemble/Docker/docassemble.crt`]: SSL certificate for HTTPS.
* <span></span>[`docassemble/Docker/docassemble.key`]: SSL certificate for HTTPS.
* <span></span>[`docassemble/Docker/docassemble.ca.pem`]: SSL certificate for HTTPS.
* <span></span>[`docassemble/Docker/docassemble.conf`]: Apache configuration file
  that causes Apache to use the Python virtualenv.
* <span></span>[`docassemble/Docker/docassemble-supervisor.conf`]: [supervisor]
  configuration file.
* <span></span>[`docassemble/Docker/docassemble.wsgi`]: WSGI server file called by
  Apache.
* <span></span>[`docassemble/Docker/docassemble.logrotate`]: This file will be copied
  into `/etc/logrotate.d` and will control the rotation of the
  **docassemble** log file in `/usr/share/docassemble/log`.
* <span></span>[`docassemble/Docker/apache.logrotate`]: This replaces the standard
  apache logrotate configuration.  It does not compress old log files,
  so that it is easier to view them in the web application.
* <span></span>[`docassemble/Docker/run-postgresql.sh`]: This is a script that is
  run by [supervisor] to start the PostgreSQL server in a
  single-server configuration.
* <span></span>[`docassemble/Docker/docassemble-syslogng.conf`]: The configuration
  for sending Apache and supervisor logs to the central log server.

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
