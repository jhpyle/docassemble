---
layout: docs
title: Installing on Docker
short_title: Docker
---

If you want to avoid having to install all of **docassemble**'s
dependencies on your server, you can run it as a [Docker] image.

It is very easy to deploy **docassemble** as a [Docker] container on
[Amazon AWS] within an [EC2] virtual machine running Amazon Linux.

[Docker] is a good platform for trying out **docassemble** for the
first time.  It can also be used as a production environment; Amazon's
[EC2 Container Service](https://aws.amazon.com/ecs/) can be used to
maintain a cluster of **docassemble** web server instances that
communicate with a central SQL server.  See
[scalability of docassemble] for information about running
**docassemble** in a multi-server arrangement.

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

The last line allows the non-root user to run Docker.  You may need to
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

# Running docassemble from a pre-packaged Docker image

**docassemble** is available on
[Docker Hub](https://hub.docker.com/r/jhpyle/docassemble/).  You can
download and run the image by doing:

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
docker exec -t -i <containerid> bash
{% endhighlight %}

You can find out the ID of the running container by doing `docker ps`.

Note that you may see some warnings, such as:

* Apache not being able to set a ulimit
* Apache not being able to determine the server's fully qualified
domain name
* Supervisor running as root
* Supervisor's unix http server running without authentication

These are nothing to worry about.

# Multi-server arrangement

To run **docassemble** in a [multi-server arrangement] using Docker,
you need to:

1. Start a single machine that will provide the SQL server;
2. Start one or more other machines that will handle the
   **docassemble** application.

{% highlight bash %}
docker run -d -p 5432:5432 jhpyle/docassemble-sql
{% endhighlight %}

Then

{% highlight bash %}
export CONTAINERROLE=webserver
docker run -d -p 80:80 -p 443:443 -p 9001:9001 -e CONTAINERROLE jhpyle/docassemble
{% endhighlight %}

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
* `docassemble/Docker/apache.conf`: note that this configuration only
  uses http, not https.
* `docassemble/Docker/config.yml`: note that this configuration sets
  `root` to `/`.

To build the image, run:

{% highlight bash %}
cd docassemble
docker build -t yourdockerhubusername/mydocassemble .
{% endhighlight %}

You can then run your image:

{% highlight bash %}
docker run -d -p 80:80 yourdockerhubusername/mydocassemble
{% endhighlight %}

Or push it to Docker Hub:

{% highlight bash %}
docker push yourdockerhubusername/mydocassemble
{% endhighlight %}

# Installing a web server on Docker

If you are using a [multi-server arrangement], you will need to feed
information about shared resources to the Docker 
Create a file `env.list` containing the access keys for SQL and S3:

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
{% endhighlight %}

{% highlight bash %}
docker run --env-file=env.list -d -p 80:80 -p 443:443 jhpyle/docassemble
{% endhighlight %}

[Docker]: https://www.docker.com/
[Amazon AWS]: http://aws.amazon.com
[docassemble repository]: {{ site.github.repository_url }}
[automated build]: https://docs.docker.com/docker-hub/builds/
[scalability of docassemble]: {{ site.baseurl }}/docs/scalability.html)
[Amazon Linux]: https://aws.amazon.com/amazon-linux-ami/
[EC2]: https://aws.amazon.com/ec2/
[multi-server arrangement]: {{ site.baseurl }}/docs/scalability.html
