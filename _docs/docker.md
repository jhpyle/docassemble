---
layout: docs
title: Installing on Docker
short_title: Docker
---

If you want to avoid having to install all of **docassemble**'s
dependencies on your server, you can run it as a [Docker] image.

[Docker] is a good platform for trying out **docassemble** for the
first time.  It can also be used as a production environment; Amazon's
[EC2 Container Service] can be used to maintain a cluster of
**docassemble** web server instances that communicate with a central
SQL server.

# Prerequisites

Make sure you have at least 16GB of storage space.  (**docassemble**
has a lot of large dependencies.)  At the end of installation, only
about 4GB will be taken up, but the installation process requires more
storage than that to be available.

# Installing Docker

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

To start docker, do:

{% highlight bash %}
sudo /etc/init.d/docker start
{% endhighlight %}

or, on systemd,

{% highlight bash %}
systemctl start docker
{% endhighlight %}

# Single-server arrangement

**docassemble** is [available on Docker Hub].  You can download and
run the image by doing:

{% highlight bash %}
docker run -d -p 80:80 -p 443:443 -p 9001:9001 jhpyle/docassemble
{% endhighlight %}

Or, if you are already using port 80 on your machine, use something
like `-p 8080:80` instead.

The image, which is about 2GB in size, is an [automated build] based
on the "master" branch of the [docassemble repository].

To make changes to the configuration, you can gain access to the
running container by running:

{% highlight bash %}
docker exec -t -i <containerid> /bin/bash
{% endhighlight %}

You can find out the ID of the running container by doing `docker ps`.

# Multi-server arrangement

To run **docassemble** in a [multi-server arrangement] using [Docker],
you need to:

1. Start a single machine that will provide the SQL server;
2. Start one or more other machines that will handle the
   **docassemble** application.

To start the SQL server, do:

{% highlight bash %}
docker run -d -p 5432:5432 jhpyle/docassemble-sql
{% endhighlight %}

Note the IP address of the [Docker] host on the local network.  You will
need to feed this address, and other information, to the [Docker]
container that responds to web requests.

Create a file `env.list` containing the access keys for SQL and [S3]:

{% highlight text %}
CONTAINERROLE=webserver
DBNAME=docassemble
DBUSER=docassemble
DBPASSWORD=abc123
DBHOST=192.168.0.56
S3ENABLE=true
S3ACCESSKEY=FWIEJFIJIDGISEJFWOEF
S3SECRETACCESSKEY=RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
S3BUCKET=yourbucketname
EC2=true
USEHTTPS=false
{% endhighlight %}

Then start the server:

{% highlight bash %}
docker run --env-file=env.list -d -p 80:80 -p 9001:9001 jhpyle/docassemble
{% endhighlight %}

See [scalability of docassemble] for information about running
**docassemble** in a multi-server arrangement.

# Creating your own Docker image

To create your own [Docker] image of docassemble, first make sure you
have git installed:

{% highlight bash %}
yum -y install git
{% endhighlight %}

Then download docassemble:

{% highlight bash %}
git clone https://github.com/jhpyle/docassemble
{% endhighlight %}

To make changes to the configuration of the **docassemble**
application that will be installed in the image, edit the following
files:

* `docassemble/Dockerfile`: you may want to change the locale and the
  Debian mirror; the standard "httpredir" mirror can lead to random
  packages not being downloaded, depending on which mirrors it chooses
  to use.
* `docassemble/Docker/config.yml`: you probably do not need to change
  this; it is a template that is updated based on the contents of the
  `--env-file` passed to `docker run`.  Once your server is up and
  running you can change the rest of the configuration in the web application.
* `docassemble/Docker/initialize.sh`: this script: updates
  `config.yml` based on the environment variables; retrieves a new
  version of `config.yml` from [S3], if available; if `CONTAINERROLE`
  is not set to `webserver`, starts the PostgreSQL server and
  initializes the database if it does not exist; creates the tables in
  the database if they do not already exist; copies SSL certificates
  from [S3] or `/usr/share/docassemble/certs`; enables the Apache
  `mod_ssl` if `USEHTTPS` is `true` and otherwise disables it; and
  starts Apache.
* `docassemble/Docker/apache.conf`: note that if `mod_ssl` is enabled,
  HTTP will merely redirect to HTTPS.
* `docassemble/Docker/docassemble.crt`: SSL certificate for HTTPS.
* `docassemble/Docker/docassemble.key`: SSL certificate for HTTPS.
* `docassemble/Docker/docassemble.ca.pem`: SSL certificate for HTTPS.
* `docassemble/Docker/docassemble.conf`: Apache configuration file
  that causes Apache to use the Python virtualenv.
* `docassemble/Docker/docassemble-supervisor.conf`: [supervisor]
  configuration file.
* `docassemble/Docker/docassemble.wsgi`: WSGI server file called by Apache.

To build the image, run:

{% highlight bash %}
cd docassemble
docker build -t yourdockerhubusername/mydocassemble .
{% endhighlight %}

You can then run your image:

{% highlight bash %}
docker run -d -p 80:80 yourdockerhubusername/mydocassemble
{% endhighlight %}

Or push it to [Docker Hub]:

{% highlight bash %}
docker push yourdockerhubusername/mydocassemble
{% endhighlight %}

[Docker]: https://www.docker.com/
[Amazon AWS]: http://aws.amazon.com
[docassemble repository]: {{ site.github.repository_url }}
[automated build]: https://docs.docker.com/docker-hub/builds/
[scalability of docassemble]: {{ site.baseurl }}/docs/scalability.html)
[Amazon Linux]: https://aws.amazon.com/amazon-linux-ami/
[EC2]: https://aws.amazon.com/ec2/
[multi-server arrangement]: {{ site.baseurl }}/docs/scalability.html
[EC2 Container Service]: https://aws.amazon.com/ecs/
[S3]: https://aws.amazon.com/s3/
[supervisor]: http://supervisord.org/
[available on Docker Hub]: https://hub.docker.com/r/jhpyle/docassemble/
[Docker Hub]: https://hub.docker.com/
