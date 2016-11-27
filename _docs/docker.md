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

# Installing Docker

If you have a Windows PC, follow the [Docker installation instructions for Windows]{:target="_blank"}.

If you have a Mac, follow the [Docker installation instructions for OS X]{:target="_blank"}.

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

Docker will probably start automatically after it is installed.  On Linux, you many need to do `sudo /etc/init.d/docker start`, `sudo systemctl start docker`, or `sudo service docker start`.

# <a name="single server arrangement"></a>Quick start

Once [Docker] is installed, you can install and run **docassemble** from the command line.

To get a command line on Windows, run [Windows PowerShell].

To get a command line on a Mac, launch the [Terminal] application.

## Starting

From the command line, simply enter:

{% highlight bash %}
docker run -d -p 80:80 jhpyle/docassemble
{% endhighlight %}

The [`docker run`] command will download and run **docassemble**,
making the application available on the standard HTTP port (port 80)
of your machine.

It will take several minutes for **docassemble** to download, and once
the [`docker run`] command finishes, **docassemble** will start to
run.  After a few minutes, you can point your web browser to the
hostname of the machine that is running [Docker].  If you are running
[Docker] on your own computer, this address is probably
http://localhost.

Using the web browser, you can log in using the default username
("admin@admin.com") and password ("password"), and make changes to the
configuration from the menu.

If you are already using port 80 on your machine, call [`docker run`]
using `-p 8080:80` instead of `-p 80:80`.

In the [`docker run`] command, the `-d` flag means that the container
will run in the background.  The `-p` flag maps a port on the host
machine to a port on the [Docker] container.  The `jhpyle/docassemble`
tag refers to an image that is [hosted on Docker Hub].  The image is
about 2.4GB in size.  It is an [automated build] based on the "master"
branch of the [docassemble repository] on [GitHub].

## Shutting down

Make sure to cleanly shut down the container by running:

{% highlight bash %}
docker stop -t 60 <containerid>
{% endhighlight %}

The container runs a [PostgreSQL] server, and the data files of the
server may become corrupted if [PostgreSQL] is not gracefully shut down.

By default, [Docker] gives containers ten seconds to shut down before
forcibly shutting them down, but sometimes [PostgreSQL] takes a little
longer than ten seconds to shut down, so it is a good idea to give the
container plenty of time to shut down gracefully.  The `-t 60` means
that [Docker] will wait up to 60 seconds before forcibly shutting down
the container.  Usually the container will shut down in about ten
seconds.

To see a list of stopped containers, run `docker ps -a`.  To remove a
container, run `docker rm <containerid>`.

## Troubleshooting

You should not need to access the running container in order to get
**docassemble** to work.  However, you might want to gain access to
the running container for some reason.

To do so, find out the ID of the running container by doing
[`docker ps`].  You will see output like the following:

{% highlight text %}
CONTAINER ID  IMAGE  COMMAND  CREATED  STATUS  PORTS  NAMES
e4fa52ba540e  jhpyle/docassemble  "/usr/bin/supervisord" ...
{% endhighlight %}

The ID is in the first column.  Then run:

{% highlight bash %}
docker exec -t -i e4fa52ba540e /bin/bash
{% endhighlight %}

using your own ID in place of `e4fa52ba540e`.  This will give you a
command prompt within the running container.

Log files on the container that you might wish to check include:

* `/var/log/supervisor/initialize-stderr---supervisor-*.log`
* `/var/log/supervisor/postgres-stderr---supervisor-*.log`
* `/var/log/apache2/error.log`
* `/usr/share/docassemble/log/docassemble.log`

Enter `exit` to leave the container and get back to your standard
command prompt.

# <a name="data storage"></a>Data storage

[Docker] containers are volatile.  They are designed to be run, turned
off, and destroyed.  When using [Docker], the best way to upgrade
**docassemble** to a new version is to destroy and rebuild your
containers.

But what about your data?  If you run **docassemble**, you are
accumulating valuable data in SQL, in files, and in [Redis].  If your
data are stored on the [Docker] container, they will be destroyed by
[`docker rm`].

There are two ways around this problem.  The first, and most
preferable solution, is to get an account on [Amazon Web Services],
create an [S3 bucket] for your data, and then when you launch your
container, set the [`S3BUCKET`] and associated
[environment variables].  When [`docker stop`] is run, **docassemble**
will backup the SQL database, the [Redis] database, the
[configuration], and your uploaded files to your [S3 bucket].  Then,
when you issue a [`docker run`] command with [environment variables]
pointing **docassemble** to your [S3 bucket], **docassemble** will
make restore from the backup.  You can [`docker rm`] your container

The second way is to use [persistent volumes], which is a feature of
[Docker].  This will store the data in directories on the [Docker]
host, so that when you destroy the container, these directories will
be untouched, and when you start up a new container, it will use the
saved directories.

These two options are explained in the following subsections.

## <a name="persistent s3"></a>Using S3

To use [S3] for persistent storage, sign up with
[Amazon Web Services], go to the [S3 Console], click "Create Bucket,"
and pick a name.  If your site is at docassemble.example.com, a good
name for the bucket is `docassemble-example-com`.  (Client software
will have trouble accessing your bucket if it contains `.`
characters.)  Under "Region," pick the region nearest you.

Then you need to obtain an access key and a secret access key for
[S3].  To obtain these credentials, go to [IAM Console] and create a
user with "programmatic access."  Under "Attach existing policies
directly," find the policy called `AmazonS3FullAccess` and attach it
to the user.

When you run a **docassemble** [Docker] container, set the
[configuration options]<span></span> [`S3BUCKET`], [`S3ACCESSKEY`],
and [`S3SECRETACCESSKEY`].

Note that if you run **docassemble** on [EC2], you can launch your
[EC2] instances with an [IAM] role that allows **docassemble** to
access to an [S3] bucket without the necessity of setting
[`S3ACCESSKEY`] and [`S3SECRETACCESSKEY`].  In this case, the only
environment variable you need to pass is [`S3BUCKET`].

These secret access keys will become available to all developers who
use your **docassemble** server, since they are in the configuration
file.  If you want to limit access to a particular bucket, you do not
have to use the `AmazonS3FullAccess` policy when obtaining [S3]
credentials.  Instead, you can create your own policy with the
following definition:

{% highlight json %}
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::docassemble-example-com"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::docassemble-example-com/*"
            ]
        }
    ]
}
{% endhighlight %}

Replace `docassemble-example-com` in the above text with the name of
your [S3] bucket.

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
-v redis:/var/lib/redis/ \
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
**docassemble** server that runs on [Docker].  For example, here is a
script that backs up all of the **docassemble** volumes running on a
remote server, `docassemble.example.com`:

{% highlight bash %}
rsync -au --rsync-path="sudo rsync" docassemble.example.com:/var/lib/docker/volumes /root/my-backup-directory
{% endhighlight %}

Note: for this to run unattended, you need to edit `~/.ssh/config` to
indicate where the identity file is located:

{% highlight text %}
Host docassemble.example.com
    HostName docassemble.example.com
    User ec2-user
    IdentityFile /root/ec2-user.pem
{% endhighlight %}

Ultimately, however, the better [data storage] solution is to
[use S3].  One of the downsides of storing the SQL server data on a
persistent volume is that if the [PostgreSQL] version changes between
one **docassemble** image and the next, the new container will not be
able to use the [PostgreSQL] data stored in the persistent volume.
The [S3] system, by contrast, uses "dump" and "restore" operations to
save the SQL database.  Also, the [`docker run`] command is much
shorter when [S3] is used.

# <a name="configuration options"></a>Configuration options

The **docassemble** [Docker] installation is configurable with
environment variables.  From the [Docker] command line, these
variables can be included with the `--env-file=env.list` option, where
`env.list` is a text file containing variable definitions in standard
shell script format.  When running **docassemble** in [ECS], these
variables are specified in [JSON] text that is entered into the web
interface.  (See the [scalability] section for more information about
using [ECS].)

Here is a sample `env.list` file:

{% highlight text %}
DAHOSTNAME=docassemble.example.com
LOCALE=en_US.UTF-8 UTF-8
TIMEZONE=America/New_York
USEHTTPS=true
USELETSENCRYPT=true
LETSENCRYPTEMAIL=admin@example.com
{% endhighlight %}

This will cause the [Apache] configuration file to use
docassemble.example.com as the `ServerName` and use [HTTPS] with
certificates hosted on [Let's Encrypt].  During startup, the `LOCALE`
will be appended to `/etc/locale.gen` and `locale-gen` and
`update-locale` will be run.  The `TIMEZONE` will be stored in
`/etc/timezone` and `dpkg-reconfigure -f noninteractive tzdata` will set the system timezone.

The available environment variables include:

* <a name="CONTAINERROLE"></a>`CONTAINERROLE`: either `all` or a
  colon-separated list of services (e.g. `web:celery`,
  `sql:log:redis`, etc.).  The options are:
  * `all`: the [Docker] container will run all of the services of
    **docassemble** on a single container.
  * `web`: The [Docker] container will serve as a web server.
  * `celery`: The [Docker] container will serve as a [Celery] node.
  * `sql`: The [Docker] container will run the central [PostgreSQL] service.
  * `redis`: The [Docker] container will run the central [Redis] service.
  * `rabbitmq`: The [Docker] container will run the central [RabbitMQ] service.
  * `log`: The [Docker] container will run the central log aggregation service.
* <a name="SERVERHOSTNAME"></a>`SERVERHOSTNAME`: If you are running
  **docassemble** in a [multi-server arrangement], and you are
  starting an application server, set this to the hostname of the
  [Docker] host.  **docassemble** will forward this address to the
  central server.  In a [multi-server arrangement], all
  **docassemble** application servers need to be able to communicate
  with each other on port 9001 (the [supervisor] port).  This is
  necessary for sending signals that cause the application servers to
  install new versions of packages, so that all servers are running
  the same software.  Note that you do not need to worry about
  `SERVERHOSTNAME` this if you are using [EC2].
* <a name="DBHOST"></a>`DBHOST`: The hostname of the [PostgreSQL]
  server.  Keep undefined or set to `null` in order to use the
  [PostgreSQL] server on the same host.  This environment variable,
  along with others that begin with `DB`, populates values in
  [`db` section] of the [configuration] file.
* <a name="DBNAME"></a>`DBNAME`: The name of the [PostgreSQL]
  database.  Default is `docassemble`.
* <a name="DBUSER"></a>`DBUSER`: The username for connecting to the
  [PostgreSQL] server.  Default is `docassemble`.
* <a name="DBPASSWORD"></a>`DBPASSWORD`: The password for connecting
  to the SQL server.  Default is `abc123`.
* <a name="DBPREFIX"></a>`DBPREFIX`: This sets the prefix for the
  database specifier.  The default is `postgresql+psycopg2://`.
* <a name="DBPORT"></a>`DBPORT`: This sets the port that
  **docassemble** will use to access the SQL server.
* <a name="DBTABLEPREFIX"></a>`DBTABLEPREFIX`: This allows multiple
  separate **docassemble** implementations to share the same SQL
  database.  The value is a prefix to be added to each table in the
  database.
* <a name="EC2"></a>`EC2`: Set this to `true` if you are running [Docker] on [EC2].
  This allows **docassemble** to determine the hostname of the server
  on which it is running.  See the [`ec2`] configuration directive.
* <a name="USEHTTPS"></a>`USEHTTPS`: Set this to `true` if you would like **docassemble** to
  communicate with the browser using encryption.  Read the [HTTPS]
  section for more information.  Defaults to `false`.  See the
  [`use https`] configuration directive.
* <a name="DAHOSTNAME"></a>`DAHOSTNAME`: Set this to the hostname by which web browsers can
  find **docassemble**.  This is necessary for [HTTPS] to
  function. See the [`external hostname`] configuration directive.
* <a name="USELETSENCRYPT"></a>`USELETSENCRYPT`: Set this to `true` if you are
  [using Let's Encrypt].  The default is `false`.  See the
  [`use lets encrypt`] configuration directive.
* <a name="LETSENCRYPTEMAIL"></a>`LETSENCRYPTEMAIL`: Set this to the e-mail address you use with
  [Let's Encrypt].  See the [`lets encrypt email`] configuration
  directive.
* <a name="LOGSERVER"></a>`LOGSERVER`: This is used in the
  [multi-server arrangement] where there is a separate server for
  collecting log messages.  The default is `none`, which causes the
  server to run [Syslog-ng].  See the [`log server`] configuration
  directive.
* <a name="REDIS"></a>`REDIS`: If you are running **docassemble** in a
  [multi-server arrangement], set this to the host name at which the
  [Redis] server can be accessed.  See the [`redis`] configuration
  directive.
* <a name="RABBITMQ"></a>`RABBITMQ`: If you are running
  **docassemble** in a [multi-server arrangement], set this to the host
  name at which the [RabbitMQ] server can be accessed.  Note that
  [RabbitMQ] is very particular about hostnames.  If the [RabbitMQ]
  server is running on a machine on which the `hostname` command
  evaluates to `abc`, then your application servers will need to set
  `RABBITMQ` to `abc` and nothing else.  It is up to you to make sure
  that `abc` resolves to an IP address.  Note that if you run
  **docassemble** using the instructions in the [scalability] section,
  you do not need to worry about this.  See the [`rabbitmq`]
  configuration directive.
* <a name="URLROOT"></a>`URLROOT`: If users access **docassemble** at
  https://docassemble.example.com, set `URLROOT` to
  `https://docassemble.example.com`.  See the [`url root`]
  configuration directive.
* <a name="BEHINDHTTPSLOADBALANCER"></a>`BEHINDHTTPSLOADBALANCER`: Set
  this to `true` if a load balancer is in use and the load balancer
  accepts connections in HTTPS but forwards them to web servers as
  HTTP.  This lets **docassemble** know that when it forms URLs, it
  should use the `https` scheme even though requests appear to be
  coming in as HTTP requests.  See the [`behind https load balancer`]
  configuration directive.
* <a name="S3ENABLE"></a>`S3ENABLE`: Set this to `true` if you are
  using [S3] as a repository for uploaded files, [Playground] files,
  the [configuration] file, and other information.  This environment
  variable, along with others that begin with `S3`, populates values
  in [`s3` section] of the [configuration] file.  If this is unset,
  but [`S3BUCKET`] is set, it will be assumed to be `true`.
* <a name="S3BUCKET"></a>`S3BUCKET`: If you are using [S3], set this
  to the bucket name.  Note that **docassemble** will not create the
  bucket for you.  You will need to create it for yourself beforehand.
* <a name="S3ACCESSKEY"></a>`S3ACCESSKEY`: If you are using [S3], set
  this to the [S3] access key.  You can ignore this environment
  variable if you are using [EC2] with an [IAM] role that allows
  access to your [S3] bucket.
* <a name="S3SECRETACCESSKEY"></a>`S3SECRETACCESSKEY`: If you are
  using [S3], set this to the [S3] access secret.  You can ignore this
  environment variable if you are using [EC2] with an [IAM] role that
  allows access to your [S3] bucket.
* <a name="TIMEZONE"></a>`TIMEZONE`: You can use this to set the time
  zone of the server.  The value of the variable is stored in
  `/etc/timezone` and `dpkg-reconfigure -f noninteractive tzdata` is
  run in order to set the system time zone.  The default is
  `America/New_York`.  See the [`timezone`] configuration directive.
* <a name="LOCALE"></a>`LOCALE`: You can use this to enable a locale
  on the server.  When the server starts, the value of `LOCALE` is
  appended to `/etc/locale.gen` and `locale-gen` and `update-locale`
  are run.  The default is `en_US.UTF-8 UTF-8`.  See the [`os locale`]
  configuration directive.
* <a name="OTHERLOCALES"></a>`OTHERLOCALES`: You can use this to set
  up other locales on the system besides the default locale.  Set this
  to a comma separated list of locales.  The values need to match
  entries in [Debian]'s `/etc/locale.gen`.  See the
  [`other os locales`] configuration directive.
* <a name="PACKAGES"></a>`PACKAGES`: If your interviews use code that
  depends on certain [Debian] packages being installed, you can
  provide a comma-separated list of [Debian] packages in the
  `PACKAGES` environment variable.  The packages will be installed
  when the image is run.  See the [`packages`] configuration
  directive.

Note that if you use [persistent volumes] and/or [S3], launching a new
**docassemble** container with different variables is not necessarily
going to change the way **docassemble** works.

For example, if [`USEHTTPS`] is `true` and [`USELETSENCRYPT`] is `true`,
then the [Apache] configuration files, if stored on a persistent
volume, will not be overwritten if they already exist when a new
container starts up.  So if you had been using [Let's Encrypt], but
then you decide to change the [`DAHOSTNAME`], you will need to delete
the saved configuration before running a new container.  If using
persistent volumes, you can run `docker volume rm letsencrypt` and
`docker volume rm apache` to remove the [Let's Encrypt] and [Apache]
configuration files.  If using [S3], you can go to the [S3 Console]
and delete the "Apache" folder and the "letsencrypt.tar.gz" file.
  
Also, if a configuration file exists on [S3] (`config.yml`) or in a
persistent volume (`/usr/share/docassemble/config/config.yml`), then
the values in that configuration will take precedence over the
corresponding environment variables that are passed to [Docker].  Once
a configuration file exists, you should make changes to the
configuration file rather than passing environment variables to
[Docker].  However, note that you always need to pass [`S3BUCKET`] if
your configuration is on [S3]; otherwise your container will not know
where to find the configuration.  Also, there are some environment
variables that do not exist in the configuration file because they are
server-specific.  These include [`CONTAINERROLE`] and
[`SERVERHOSTNAME`].

# <a name="multi server arrangement"></a>Multi-server arrangement

## Services on different machines

The **docassemble** application consists of several services, some of
which are singular and some of which can be plural.

The singular services include:

* SQL
* [Redis]
* [RabbitMQ] for coordinating [background processes]
* The **docassemble** log message aggregator

The (potentially) plural services include:

* Web servers
* [Celery] nodes

The **docassemble** [Docker] container will run any subset of these
six services, depending on the value of the environment variable
[`CONTAINERROLE`], which is passed to the container at startup.  In a
single-server arrangement ([`CONTAINERROLE`] = `all`, or left
undefined), the container runs all of the services (except the log
message aggregator, which is not necessary in the case of a
single-server arrangement).

You can run **docassemble** in a [multi-server arrangement] using
[Docker] by running the **docassemble** image on different hosts using
different [configuration options].

In a multi-server arrangement, you can have one machine run SQL,
another machine run [Redis] and [RabbitMQ], and any number of machines
run web servers and [Celery] nodes.  You can decide how to allocate
services to different machines.  For example, you might want to run
central tasks on a powerful server, while running many web servers on
less powerful machines.

Since the SQL, [Redis], and [RabbitMQ] services are standard services,
they do not have to be run from **docassemble** [Docker] containers.

To change the SQL server that **docassemble** uses, edit the
[`DBHOST`], [`DBNAME`], [`DBUSER`], [`DBPASSWORD`], [`DBPREFIX`],
[`DBPORT`], and [`DBTABLEPREFIX`] [configuration options].

To change the [Redis] server that **docassemble** uses, edit the
[`REDIS`] [configuration option].

To change the [RabbitMQ] server that **docassemble** uses, edit the
[`RABBITMQ`] [configuration option].

## Port opening

Note that for every service that a [Docker] container provides,
appropriate ports need to be forwarded from the [Docker] host machine
to the container.

* Regardless of the [`CONTAINERROLE`], port 9001 needs to be forwarded
  so that the container can be controlled via [supervisor].
* If [`CONTAINERROLE`] includes `sql`: forward port 5432 ([Postgresql])
* If [`CONTAINERROLE`] includes `web`: forward ports 80 (HTTP) and 443 (HTTPS)
* If [`CONTAINERROLE`] includes `log`: forward ports 514 ([Syslog-ng])
  and 8080 (custom web server)
* If [`CONTAINERROLE`] includes `redis`: forward port 6379 ([Redis])
* If [`CONTAINERROLE`] includes `rabbitmq`: forward ports 4369, 5671,
  5672, and 25672 ([RabbitMQ]).

For example:

{% highlight bash %}
docker run \
-e CONTAINERROLE=sql:redis \
...
-d -p 5432:5432 -p 6379:6379 -p 9001:9001 \
jhpyle/docassemble
{% endhighlight %}

{% highlight bash %}
docker run \
-e CONTAINERROLE=web:celery \
...
-d -p 80:80 -p 443:443 -p 9001:9001 \
jhpyle/docassemble
{% endhighlight %}

## File sharing

If you run multiple **docassemble** [Docker] containers on different
machines, the containers will need to have a way to share files with
one another.

One way to share files among containers is to make
`/usr/share/docassemble/` a [persistent volume] on a network file
system.  This directory contains the configuration, SSL certificates,
[Python virtual environment], and uploaded files.  However, network
file systems present problems.

A preferable way to share files is with [Amazon S3], which
**docassemble** supports.  See the [using S3] section for instructions
on setting this up.

## Configuration file

Note that when you use [S3] for [data storage], **docassemble** will
copy the `config.yml` file out of [S3] on startup, and save
`config.yml` to [S3] whenever the configuration is modified.

This means that as long as there is a `config.yml` file on [S3] with
the configuration you want, you can start **docassemble** containers
without specifying a lot of [configuration options]; you simply have
to refer to the [S3] bucket, and **docassemble** will take it from
there.  For example, to run a central server, you can do:

{% highlight bash %}
docker run \
-e CONTAINERROLE=sql:log:redis:rabbitmq \
-e S3BUCKET=docassemble-example-com \
-e S3ACCESSKEY=FWIEJFIJIDGISEJFWOEF \
-e S3SECRETACCESSKEY=RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG \
-d -p 80:8080 -p 5432:5432 -p 514:514 \
-p 6379:6379 -p 4369:4369 -p 5671:5671 \
-p 5672:5672 -p 25672:25672 -p 9001:9001 \
jhpyle/docassemble
{% endhighlight %}

To run an application server, you can do:

{% highlight bash %}
docker run \
-e CONTAINERROLE=web:celery \
-e S3BUCKET=docassemble-example-com \
-e S3ACCESSKEY=FWIEJFIJIDGISEJFWOEF \
-e S3SECRETACCESSKEY=RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG \
-d -p 80:80 -p 443:443 -p 9001:9001 \
jhpyle/docassemble
{% endhighlight %}

# <a name="https"></a>Using HTTPS

If you are running **docassemble** on [EC2], the easiest way to enable
HTTPS support is to set up an [Application Load Balancer] that accepts
connections in HTTPS format and forwards them to the web servers in
HTTP format.  In this configuration [Amazon] takes care of creating
and hosting the necessary SSL certificates.

If you are not using a [load balancer], you can use HTTPS either by
setting up [Let's Encrypt] or by providing your own certificates.

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
USEHTTPS=true
DAHOSTNAME=docassemble.example.com
USELETSENCRYPT=true
LETSENCRYPTEMAIL=admin@example.com
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

Using your own SSL certificates with [Docker] requires that your SSL
certificates reside within each container.  There are several ways to
accomplish this:

* Use [S3] and upload the certificates to your bucket.
* Use [persistent volumes] and copy the SSL certificate files
  (`docassemble.key`, `docassemble.crt`, and `docassemble.ca.pem`)
  into the volume for `/usr/share/docassemble/certs` before starting
  the container.
* [Build your own private image] in which your SSL certificates are
  placed in `Docker/docassemble.key`, `Docker/docassemble.crt`, and
  `Docker/docassemble.ca.pem`.  During the build process, these files
  will be copied into `/usr/share/docassemble/certs`.

The default Apache configuration file expects SSL certificates to be
located in the following files:

{% highlight text %}
SSLCertificateFile /etc/ssl/docassemble/docassemble.crt
SSLCertificateKeyFile /etc/ssl/docassemble/docassemble.key 
SSLCertificateChainFile /etc/ssl/docassemble/docassemble.ca.pem
{% endhighlight %}

The meaning of these files is as follows:

* `docassemble.crt`: this file is generated by your certificate
  authority when you submit a certificate signing request.
* `docassemble.key`: this file is generated at the time you create
  your certificate signing request.
* `docassemble.ca.pem`: this file is generated by your certificate
  authority.  It is variously known as the "chain file"
  or the "root bundle."

In order to make sure that these files are replicated on every web
server, the [supervisor] will run the
`docassemble.webapp.install_certs` module before starting the web
server.

If you are using [S3], this module will copy the files from the
`certs/` prefix in your bucket to `/etc/ssl/docassemble`.  You can use
the [S3 Console] to create a folder called `certs` and upload your
certificate files into that folder.

If you are not using [S3], the `docassemble.webapp.install_certs`
module will copy the files from `/usr/share/docassemble/certs` to
`/etc/ssl/docassemble`.

There are two ways that you can put your own certificate files into
the `/usr/share/docassemble/certs` directory.  The first way is to
[create your own Docker image] of **docassemble** and put your
certificates into the `Docker/ssl` directory.  The contents of this
directory are copied into `/usr/share/docassemble/certs` during the
build process.

The second way is to use [persistent volumes].  If you have a
persistent volume called `certs` for the directory
`/usr/share/docassemble/certs`, then you can run `docker volume
inspect certs` to get the directory on the [Docker] host corresponding
to this directory, and you can copy the SSL certificate files into
that directory before starting the container.

Note that the files need to be called `docassemble.crt`,
`docassemble.key`, and `docassemble.ca.pem`, because this is what the
standard web server configuration expects.

If you want to use different filesystem or S3 locations, the
`docassemble.webapp.install_certs` can be configured to use different
locations.  See the [configuration] variables [`certs`] and
[`cert_install_directory`].

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
* <span></span>[`docassemble/Docker/config/config.yml.dist`]: you probably do not need to change
  this; it is a template that is updated based on the contents of the
  `--env-file` passed to [`docker run`].  Once your server is up and
  running you can change the rest of the configuration in the web
  application.
* <span></span>[`docassemble/Docker/initialize.sh`]: this script
  updates `config.yml` based on the environment variables; retrieves a
  new version of `config.yml` from [S3], if available; if
  [`CONTAINERROLE`] is not set to `webserver`, starts the [PostgreSQL]
  server and initializes the database if it does not exist; creates
  the tables in the database if they do not already exist; copies SSL
  certificates from [S3] or `/usr/share/docassemble/certs` if [S3] is
  not enabled; enables the [Apache] `mod_ssl` if `USEHTTPS` is `true`
  and otherwise disables it; runs the [Let's Encrypt] utility if
  `USELETSENCRYPT` is `true` and the utility has not been run yet; and
  starts [Apache].
* <span></span>[`docassemble/Docker/config/docassemble-http.conf`]:
  [Apache] configuration file for handling HTTP requests.
  Note that if `mod_ssl` is enabled, HTTP will merely redirect to
  HTTPS.
* <span></span>[`docassemble/Docker/config/docassemble-ssl.conf`]:
  [Apache] configuration file for handling HTTPS requests.
* <span></span>[`docassemble/Docker/config/docassemble-log.conf`]:
  [Apache] configuration file for handling requests on port 8080.
  This is enabled if the [`CONTAINERROLE`] includes `log`.
* <span></span>[`docassemble/Docker/ssl/docassemble.crt`]: SSL certificate for HTTPS.
* <span></span>[`docassemble/Docker/ssl/docassemble.key`]: SSL certificate for HTTPS.
* <span></span>[`docassemble/Docker/ssl/docassemble.ca.pem`]: SSL certificate for HTTPS.
* <span></span>[`docassemble/Docker/docassemble.conf`]: [Apache] configuration file
  that causes [Apache] to use the [Python virtualenv].
* <span></span>[`docassemble/Docker/docassemble-supervisor.conf`]: [supervisor]
  configuration file.
* <span></span>[`docassemble/Docker/docassemble-syslog-ng.conf`]: [Syslog-ng]
  configuration file used when [`CONTAINERROLE`] does not include `log`.
* <span></span>[`docassemble/Docker/syslog-ng.conf`]: [Syslog-ng]
  configuration file used when [`CONTAINERROLE`] includes `log`.
* <span></span>[`docassemble/Docker/rabbitmq.config`]: [RabbitMQ]
  configuration file.
* <span></span>[`docassemble/Docker/docassemble.wsgi`]: WSGI server file called by
  [Apache].
* <span></span>[`docassemble/Docker/docassemble.logrotate`]: This file will be copied
  into `/etc/logrotate.d` and will control the rotation of the
  **docassemble** log file in `/usr/share/docassemble/log`.
* <span></span>[`docassemble/Docker/apache.logrotate`]: This replaces the standard
  apache logrotate configuration.  It does not compress old log files,
  so that it is easier to view them in the web application.
* <span></span>[`docassemble/Docker/run-apache.sh`]: This is a script
  that is run by [supervisor] to start the [Apache] server.
* <span></span>[`docassemble/Docker/run-cron.sh`]: This is a script
  that is run by [supervisor] to start the [cron] daemon.
* <span></span>[`docassemble/Docker/run-postgresql.sh`]: This is a script that is
  run by [supervisor] to start the [PostgreSQL] server.
* <span></span>[`docassemble/Docker/run-rabbitmq.sh`]: This is a script that is
  run by [supervisor] to start the [RabbitMQ] server.
* <span></span>[`docassemble/Docker/run-redis.sh`]: This is a script that is
  run by [supervisor] to start the [Redis] server.
* <span></span>[`docassemble/Docker/sync.sh`]: This is a script that is
  run by [supervisor] to synchronize log files.

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

# Cleaning up after multiple builds

If you build docker images, you may find your disk space being used
up.  These three lines will stop all containers, remove all
containers, and then remove all of the images that [Docker] created
during the build process.

{% highlight bash %}
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images | grep "^<none>" | awk "{print $3}")
{% endhighlight %}

# Upgrading docassemble when using Docker

As new versions of **docassemble** become available, you can obtain
the latest version by running:

{% highlight bash %}
docker pull jhpyle/docassemble
{% endhighlight %}

Then, subsequent [`docker run`] and [`docker build`] commands will use
the latest **docassemble** image.

When you are using [Docker] to run **docassemble**, you can upgrade
**docassemble** to the newest version simply by running [`docker stop`]
and [`docker rm`] on the **docassemble** container.  Note that [`docker rm`] will delete all of the data on the server unless you are using a [data storage] system.

[Redis]: http://redis.io/
[Docker installation instructions for Windows]: https://docs.docker.com/engine/installation/windows/
[Docker installation instructions for OS X]: https://docs.docker.com/engine/installation/mac/
[Docker]: https://www.docker.com/
[Amazon AWS]: http://aws.amazon.com
[automated build]: https://docs.docker.com/docker-hub/builds/
[scalability of docassemble]: {{ site.baseurl }}/docs/scalability.html
[Amazon Linux]: https://aws.amazon.com/amazon-linux-ami/
[EC2]: https://aws.amazon.com/ec2/
[single-server arrangement]: #single server arrangement
[multi-server arrangement]: #multi server arrangement
[EC2 Container Service]: https://aws.amazon.com/ecs/
[S3]: https://aws.amazon.com/s3/
[supervisor]: http://supervisord.org/
[hosted on Docker Hub]: https://hub.docker.com/r/jhpyle/docassemble/
[Docker Hub]: https://hub.docker.com/
[scalability]: {{ site.baseurl }}/docs/scalability.html
[Amazon S3]: https://aws.amazon.com/s3/
[using HTTPS]: {{ site.baseurl }}/docs/scalability.html#ssl
[docassemble repository]: {{ site.github.repository_url }}
[`docassemble/Dockerfile`]: {{ site.github.repository_url }}/blob/master/Dockerfile
[`docassemble/Docker/config/config.yml.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/config.yml.dist
[`docassemble/Docker/initialize.sh`]: {{ site.github.repository_url }}/blob/master/Docker/initialize.sh
[`docassemble/Docker/config/docassemble-http.conf`]: {{ site.github.repository_url }}/blob/master/Docker/config/docassemble-http.conf
[`docassemble/Docker/config/docassemble-ssl.conf`]: {{ site.github.repository_url }}/blob/master/Docker/config/docassemble-ssl.conf
[`docassemble/Docker/config/docassemble-log.conf`]: {{ site.github.repository_url }}/blob/master/Docker/config/docassemble-log.conf
[`docassemble/Docker/ssl/docassemble.crt`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/docassemble.crt
[`docassemble/Docker/ssl/docassemble.key`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/docassemble.key
[`docassemble/Docker/ssl/docassemble.ca.pem`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/docassemble.ca.pem
[`docassemble/Docker/docassemble.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.conf
[`docassemble/Docker/docassemble-supervisor.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble-supervisor.conf
[`docassemble/Docker/docassemble-syslog-ng.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble-syslog-ng.conf
[`docassemble/Docker/syslog-ng.conf`]: {{ site.github.repository_url }}/blob/master/Docker/syslog-ng.conf
[`docassemble/Docker/rabbitmq.config`]: {{ site.github.repository_url }}/blob/master/Docker/rabbitmq.config
[`docassemble/Docker/docassemble.wsgi`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.wsgi
[`docassemble/Docker/docassemble.logrotate`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.logrotate
[`docassemble/Docker/apache.logrotate`]: {{ site.github.repository_url }}/blob/master/Docker/apache.logrotate
[`docassemble/Docker/run-postgresql.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-postgresql.sh
[`docassemble/Docker/run-apache.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-apache.sh
[`docassemble/Docker/run-cron.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-cron.sh
[`docassemble/Docker/run-rabbitmq.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-rabbitmq.sh
[`docassemble/Docker/run-redis.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-redis.sh
[`docassemble/Docker/sync.sh`]: {{ site.github.repository_url }}/blob/master/Docker/sync.sh
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
[persistent volume]: #persistent
[configuration]: {{ site.baseurl }}/docs/config.html
[`db` section]: {{ site.baseurl }}/docs/config.html#db
[`s3` section]: {{ site.baseurl }}/docs/config.html#s3
[Build your own private image]: #build
[Redis]: http://redis.io/
[RabbitMQ]: https://www.rabbitmq.com/
[Application Load Balancer]: https://aws.amazon.com/elasticloadbalancing/applicationloadbalancer/
[IAM]: https://aws.amazon.com/iam/
[Amazon]: https://amazon.com
[load balancer]: https://en.wikipedia.org/wiki/Load_balancing_(computing)
[S3 Console]: https://console.aws.amazon.com/s3/home
[IAM Console]: https://console.aws.amazon.com/iam
[create your own Docker image]: #build
[`certs`]: {{ site.baseurl }}/docs/config.html#certs
[`cert_install_directory`]: {{ site.baseurl }}/docs/config.html#cert_install_directory
[cron]: https://en.wikipedia.org/wiki/Cron
[Python virtual environment]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[configuration options]: #configuration options
[configuration option]: #configuration options
[`DBHOST`]: #DBHOST
[`DBNAME`]: #DBNAME
[`DBUSER`]: #DBUSER
[`DBPASSWORD`]: #DBPASSWORD
[`DBPREFIX`]: #DBPREFIX
[`DBPORT`]: #DBPORT
[`DBTABLEPREFIX`]: #DBTABLEPREFIX
[`REDIS`]: #REDIS
[`RABBITMQ`]: #RABBITMQ
[`LOGSERVER`]: #LOGSERVER
[`S3BUCKET`]: #S3BUCKET
[`S3ACCESSKEY`]: #S3ACCESSKEY
[`S3SECRETACCESSKEY`]: #S3SECRETACCESSKEY
[`CONTAINERROLE`]: #CONTAINERROLE
[`SERVERHOSTNAME`]: #SERVERHOSTNAME
[`DAHOSTNAME`]: #DAHOSTNAME
[`USEHTTPS`]: #USEHTTPS
[`USELETSENCRYPT`]: #USELETSENCRYPT
[Celery]: http://www.celeryproject.org/
[background processes]: {{ site.baseurl }}/docs/functions.html#background
[Windows PowerShell]: https://en.wikipedia.org/wiki/PowerShell
[Terminal]: https://en.wikipedia.org/wiki/Terminal_(macOS)
[`timezone`]: {{ site.baseurl }}/docs/config.html#timezone
[`os locale`]: {{ site.baseurl }}/docs/config.html#os locale
[`other os locales`]: {{ site.baseurl }}/docs/config.html#other os locales
[`packages`]: {{ site.baseurl }}/docs/config.html#packages
[`behind https load balancer`]: {{ site.baseurl }}/docs/config.html#behind https load balancer
[`rabbitmq`]: {{ site.baseurl }}/docs/config.html#rabbitmq
[`redis`]: {{ site.baseurl }}/docs/config.html#redis
[`log server`]: {{ site.baseurl }}/docs/config.html#log server
[`lets encrypt email`]: {{ site.baseurl }}/docs/config.html#lets encrypt email
[`use lets encrypt`]: {{ site.baseurl }}/docs/config.html#use lets encrypt
[`external hostname`]: {{ site.baseurl }}/docs/config.html#external hostname
[`use https`]: {{ site.baseurl }}/docs/config.html#use https
[`ec2`]: {{ site.baseurl }}/docs/config.html#ec2
[`packages`]: {{ site.baseurl }}/docs/config.html#packages
[`url root`]: {{ site.baseurl }}/docs/config.html#url root
[Debian]: https://www.debian.org/
[using S3]: #persistent s3
[use S3]: #persistent s3
[environment variables]: #configuration options
[GitHub]: https://github.com
[data storage]: #data storage
[`docker stop`]: https://docs.docker.com/engine/reference/commandline/stop/
[`docker rm`]: https://docs.docker.com/engine/reference/commandline/rm/
[`docker run`]: https://docs.docker.com/engine/reference/commandline/run/
[`docker build`]: https://docs.docker.com/engine/reference/commandline/build/
[`docker ps`]: https://docs.docker.com/engine/reference/commandline/ps/
[Amazon Web Services]: https://aws.amazon.com
[S3 bucket]: http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
