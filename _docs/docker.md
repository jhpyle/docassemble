---
layout: docs
title: Installing on Docker
short_title: Docker
---

[Docker] is a good platform for trying out **docassemble** for the
first time.  It is also ideal in a production environment.

Amazon's [EC2 Container Service] can be used to maintain a cluster of
**docassemble** web server instances, created from [Docker] images,
that communicate with a central server.  For information about how to
install **docassemble** in a multi-server arrangement on
[EC2 Container Service] ("[ECS]"), see the [scalability] section.

# Choosing where to run Docker

[Docker] can be run on a Windows PC, a Mac, an on-site Linux machinne,
or a Linux-based virtual machine in the cloud.  Since **docassemble**
is a web application, the ideal platform is a Linux virtual machine in
the cloud.  You can test out **docassemble** on a PC or a Mac, but for
serious, long-term deployment, it is probably worthwhile to run it in
the cloud.

If you have never deployed a Linux-based virtual machine in the cloud
before, this might be a good opportunity to learn.  The ability to use
virtual machines on a cloud provider like [Amazon Web Services] or
[Microsoft Azure] is a valuable and transferable skill.  Learning how
to do cloud computing is beyond the scope of this documentation, but
there are many guides on the internet.  The basic steps of running
Docker in the cloud are:

1. Create an account with a cloud computing provider.
2. Start a [sufficiently powerful](#install) virtual machine that runs
   some flavor of Linux.
3. Connect to the virtual machine using [SSH] in order to control it
   using a command line.  This can be a complicated step because most
   providers use certificates rather than passwords for authentication.
4. [Install Docker](#install) on the virtual machine.

There are also methods of controlling cloud computing resources from a
local command line, where you type special commands to deploy [Docker]
containers.  These can be very useful, but they tend to be more
complicated to use than the basic [Docker] command line.

# <a name="install"></a>Installing Docker

First, make sure you are running [Docker] on a computer or virtual
computer with at least 2GB of memory and 20GB of hard drive space.

If you have a Windows PC, follow the
[Docker installation instructions for Windows]{:target="_blank"}.  You
will need administrator access on your PC in order to install (or
upgrade) Docker.

If you have a Mac, follow the [Docker installation instructions for OS X]{:target="_blank"}.

On Ubuntu (assuming username `ubuntu`):

{% highlight bash %}
sudo apt-get -y update
sudo apt-get -y install docker.io
sudo usermod -a -G docker ubuntu
{% endhighlight %}

On [Amazon Linux] (assuming the username `ec2-user`):

{% highlight bash %}
sudo yum -y update
sudo yum -y install docker
sudo usermod -a -G docker ec2-user
{% endhighlight %}

The `usermod` line allows the non-root user to run [Docker].  You may
need to log out and log back in again for this new user permission to
take effect.

[Docker] will probably start automatically after it is installed.  On
Linux, you many need to do `sudo /etc/init.d/docker start`, `sudo
systemctl start docker`, or `sudo service docker start`.

# <a name="single server arrangement"></a>Quick start

Once [Docker] is installed, you can install and run **docassemble** from the command line.

To get a command line on Windows, run [Windows PowerShell].

To get a command line on a Mac, launch the [Terminal] application.

To get a command line on a virtual machine in the cloud, follow your
provider's instructions for using [SSH] to connect to your machine.

## Starting

From the command line, simply type in:

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

If you are running [Docker] on [AWS], the address will be something
like `http://ec2-52-38-111-32.us-west-2.compute.amazonaws.com` (check
your [EC2] configuration for the hostname).  On [AWS], you will need a
[Security Group] that opens [HTTP] (port 80) to the outside world in
order to allow web browsers to connect to your [EC2] instance.

Using the web browser, you can log in using the default username
("admin@admin.com") and password ("password"), and make changes to the
configuration from the menu.

In the [`docker run`] command, the `-d` flag means that the container
will run in the background.

The `-p` flag maps a port on the host machine to a port on the
[Docker] container.  In this example, port 80 on the host machine will
map to port 80 within the [Docker] container.  If you are already
using port 80 on the host machine, you could use `-p 8080:80`, and
then port 8080 on the host machine would be passed through to port 80
on the [Docker] container.

The `jhpyle/docassemble` tag refers to a [Docker] image that is
[hosted on Docker Hub].  The image is about 2GB in size, and when it
runs, the container uses about 10GB of hard drive space.  The
`jhpyle/docassemble` image is based on the "master" branch of the
[docassemble repository] on [GitHub].  It is rebuilt every time the
minor version of **docassemble** increases.

## Shutting down

Shut down the container by running:

{% highlight bash %}
docker stop -t 60 <containerid>
{% endhighlight %}

By default, [Docker] gives containers ten seconds to shut down before
forcibly shutting them down.  Usually, ten seconds is plenty of time,
but if the server is slow, **docassemble** might take a little longer
than ten seconds to shut down.  To be on the safe side, give the
container plenty of time to shut down gracefully.  The `-t 60` means
that [Docker] will wait up to 60 seconds before forcibly shutting down
the container.  It will probably take no more than 15 seconds for the
[`docker stop`] command to complete.

It is very important to avoid a forced shutdown of **docassemble**.
The container runs a [PostgreSQL] server, and the data files of the
server may become corrupted if [PostgreSQL] is not gracefully shut
down.  To facilitate [data storage] (more on this later),
**docassemble** backs up your data during the shutdown process and
restores from that backup during the initialization process.  If the
shutdown process is interrupted, your data may be left in an
inconsistent state and there may be errors during later
initialization.

To see a list of stopped containers, run `docker ps -a`.  To remove a
container, run `docker rm <containerid>`.

## Troubleshooting

You should not need to access the running container in order to get
**docassemble** to work, and all the log files you need will hopefully
be available from "Logs" in the web browser.  However, you might want
to gain access to the running container for some reason.

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

The first thing to check when you connect to a container is:

{% highlight bash %}
supervisorctl status
{% endhighlight %}

The output should be something like:

{% highlight text %}
apache2                          RUNNING   pid 1088, uptime 0:14:15
celery                           RUNNING   pid 1865, uptime 0:14:45
cron                             STOPPED   Not started
initialize                       RUNNING   pid 1014, uptime 0:14:53
postgres                         RUNNING   pid 1020, uptime 0:14:42
rabbitmq                         RUNNING   pid 1045, uptime 0:14:38
redis                            RUNNING   pid 1067, uptime 0:14:35
reset                            STOPPED   Not started
sync                             EXITED    Dec 22 07:22 AM
syslogng                         STOPPED   Not started
update                           STOPPED   Not started
watchdog                         RUNNING   pid 1013, uptime 0:14:53
websockets                       RUNNING   pid 1904, uptime 0:14:40
{% endhighlight %}

If you are running **docassemble** in a single-server arrangement, the
processes that should be "RUNNING" include apache2, celery,
initialize, postgres, rabbitmq, redis, watchdog, and websockets.

Log files on the container that you might wish to check include:

* `/var/log/supervisor/initialize-stderr---supervisor-*.log`
* `/var/log/supervisor/postgres-stderr---supervisor-*.log`
* Other files in `/var/log/supervisor/`
* `/var/log/apache2/error.log`
* `/usr/share/docassemble/log/docassemble.log`

Enter `exit` to leave the container and get back to your standard
command prompt.

# <a name="configuration options"></a>Configuration options

In the example [above](#single server arrangement), we started
**docassemble** with `docker run -d -p 80:80 jhpyle/docassemble`.
This command will cause **docassemble** to use default values for all
configuration options.  You can also communicate specific
configuration options to the container.

The recommended way to do this is to create a text file called
`env.list` in the current working directory containing environment
variable definitions in standard shell script format.  For example:

{% highlight text %}
DAHOSTNAME=docassemble.example.com
USEHTTPS=true
USELETSENCRYPT=true
LETSENCRYPTEMAIL=admin@example.com
{% endhighlight %}

Then, you can pass these environment variables to the container using
the [`docker run`] command:

{% highlight bash %}
docker run --env-file=env.list -d -p 80:80 -p 443:443 jhpyle/docassemble
{% endhighlight %}

These configuration options will cause the [Apache] configuration file
to use docassemble.example.com as the `ServerName` and use [HTTPS]
with certificates hosted on [Let's Encrypt].  (The directive `-p
443:443` is included so that the [HTTPS] port is exposed.)

A [template for the `env.list` file] is included in distribution.

When running **docassemble** in [ECS], environment variables like
these are specified in [JSON] text that is entered into the web
interface.  (See the [scalability] section for more information about
using [ECS].)

In your `env.list` file, you can set a variety of options.

The following two options are specific to the particular server being
started (which, in a [multi-server arrangement], will vary from server
to server).

* <a name="CONTAINERROLE"></a>`CONTAINERROLE`: either `all` or a
  colon-separated list of services (e.g. `web:celery`,
  `sql:log:redis`, etc.) that should be started by the server.  The
  available options are:
  * `all`: the [Docker] container will run all of the services of
    **docassemble** on a single container.
  * `web`: The [Docker] container will serve as a web server.
  * `celery`: The [Docker] container will serve as a [Celery] node.
  * `sql`: The [Docker] container will run the central [PostgreSQL] service.
  * `redis`: The [Docker] container will run the central [Redis] service.
  * `rabbitmq`: The [Docker] container will run the central [RabbitMQ] service.
  * `log`: The [Docker] container will run the central log aggregation service.
  * `mail`: The [Docker] container will run [Exim] in order to accept [e-mails].
* <a name="SERVERHOSTNAME"></a>`SERVERHOSTNAME`: In a
  [multi-server arrangement], all **docassemble** application servers
  need to be able to communicate with each other using port 9001 (the
  [supervisor] port).  All application servers "register" with the
  central SQL server.  When they register, they each provide their
  hostname; that is, the hostname at which the specific individual
  application server can be found.  Then, when an application server
  wants to send a message to the other application servers, the
  application server can query the central SQL server to get a list of
  hostnames of other application servers.  This is necessary so that
  any one application server can send a signal to the other
  application servers to install a new package or a new version of a
  package, so that all servers are running the same software.  If you
  are running **docassemble** in a [multi-server arrangement], and you
  are starting an application server, set `SERVERHOSTNAME` to the
  hostname with which other application servers can find that server.
  Note that you do not need to worry about setting `SERVERHOSTNAME` if
  you are using [EC2], because [Docker] containers running on [EC2]
  can discover their actual hostnames by querying a specific IP
  address.

The other options you can set in `env.list` are global for your entire
**docassemble** installation, rather than specific to the server being
started.

The following eight options indicate where an existing configuration
file can be found on [S3](#persistent s3) or
[Azure blob storage](#persistent azure).  If a [configuration] file
exists in the cloud at the indicated location, that [configuration]
file will be used to set the [configuration] of your **docassemble**
installation.  If no [configuration] file yet exists in the cloud at the
indicated location, **docassemble** will create an initial
[configuration] file and store it in the indicated location.

* <a name="S3ENABLE"></a>`S3ENABLE`: Set this to `True` if you are
  using [S3] as a repository for uploaded files, [Playground] files,
  the [configuration] file, and other information.  This environment
  variable, along with others that begin with `S3`, populates values
  in [`s3` section] of the initial [configuration] file.  If this is
  unset, but [`S3BUCKET`] is set, it will be assumed to be `True`.
* <a name="S3BUCKET"></a>`S3BUCKET`: If you are using [S3], set this
  to the bucket name.  Note that **docassemble** will not create the
  bucket for you.  You will need to create it for yourself
  beforehand.  The bucket should be empty.
* <a name="S3ACCESSKEY"></a>`S3ACCESSKEY`: If you are using [S3], set
  this to the [S3] access key.  You can ignore this environment
  variable if you are using [EC2] with an [IAM] role that allows
  access to your [S3] bucket.
* <a name="S3SECRETACCESSKEY"></a>`S3SECRETACCESSKEY`: If you are
  using [S3], set this to the [S3] access secret.  You can ignore this
  environment variable if you are using [EC2] with an [IAM] role that
  allows access to your [S3] bucket.
* <a name="S3REGION"></a>`S3REGION`: If you are using [S3], set this
  to the [region] you are using (e.g., `us-west-1`, `us-west-2`,
  `ca-central-1`).
* <a name="AZUREENABLE"></a>`AZUREENABLE`: Set this to `True` if you
  are using [Azure blob storage](#persistent azure) as a repository
  for uploaded files, [Playground] files, the [configuration] file,
  and other information.  This environment variable, along with others
  that begin with `AZURE`, populates values in [`azure` section] of
  the [configuration] file.  If this is unset, but
  [`AZUREACCOUNTNAME`], [`AZUREACCOUNTKEY`], and [`AZURECONTAINER`]
  are set, it will be assumed to be `True`.
* <a name="AZURECONTAINER"></a>`AZURECONTAINER`: If you are using
  [Azure blob storage](#persistent azure), set this to the container
  name.  Note that **docassemble** will not create the container for you.
  You will need to create it for yourself beforehand.
* <a name="AZUREACCOUNTNAME"></a>`AZUREACCOUNTNAME`: If you are using
  [Azure blob storage](#persistent azure), set this to the account
  name.
* <a name="AZUREACCOUNTKEY"></a>`AZUREACCOUNTKEY`: If you are
  using [Azure blob storage], set this to the account key.

The following options are "setup" parameters that are useful for
pre-populating a fresh [configuration] with particular values.  These
environment variables are effective only during an initial `run` of
the [Docker] container, when a [configuration] file does not already
exist.

Note: if you are using [persistent volumes], or you have set the
options above for 
[S3](#persistent s3)/[Azure blob storage](#persistent azure) 
and a [configuration] file exists in your cloud storage, the values 
in that [configuration] file will take precedence over any values you 
specify in `env.list`.

Moreover, some of the values listed below are only used when
generating the initial [Apache] configuration files.  To make changes
to [Apache] configuration files after they have been created, edit the
files directly.  If you are using [S3](#persistent
s3)/[Azure blob storage](#persistent azure), you can edit these
configuration files in the cloud and then stop and start your
container for the new configuration to take effect.

* <a name="DBHOST"></a>`DBHOST`: The hostname of the [PostgreSQL]
  server.  Keep undefined or set to `null` in order to use the
  [PostgreSQL] server on the same host.  This environment variable,
  along with others that begin with `DB`, populates values in
  [`db` section] of the [configuration] file.
* <a name="DBNAME"></a>`DBNAME`: The name of the [PostgreSQL]
  database.  The default is `docassemble`.
* <a name="DBUSER"></a>`DBUSER`: The username for connecting to the
  [PostgreSQL] server.  The default is `docassemble`.
* <a name="DBPASSWORD"></a>`DBPASSWORD`: The password for connecting
  to the SQL server.  The default is `abc123`.  The password cannot
  contain the character `#`.
* <a name="DBPREFIX"></a>`DBPREFIX`: This sets the prefix for the
  database specifier.  The default is `postgresql+psycopg2://`.
* <a name="DBPORT"></a>`DBPORT`: This sets the port that
  **docassemble** will use to access the SQL server.  If you are using
  the default port for your database backend, you do not need to set
  this.
* <a name="DBTABLEPREFIX"></a>`DBTABLEPREFIX`: This allows multiple
  separate **docassemble** implementations to share the same SQL
  database.  The value is a prefix to be added to each table in the
  database.
* <a name="EC2"></a>`EC2`: Set this to `True` if you are running
  [Docker] on [EC2].  This tells **docassemble** that it can use an
  [EC2]-specific method of determining the hostname of the server on
  which it is running.  See the [`ec2`] configuration directive.
* <a name="USEHTTPS"></a>`USEHTTPS`: Set this to `True` if you would
  like **docassemble** to communicate with the browser using
  encryption.  Read the [HTTPS] section for more information.
  Defaults to `False`.  See the [`use https`] configuration directive.
* <a name="DAHOSTNAME"></a>`DAHOSTNAME`: Set this to the hostname by
  which web browsers can find **docassemble**.  This is necessary for
  [HTTPS] to function. See the [`external hostname`] configuration
  directive.
* <a name="USELETSENCRYPT"></a>`USELETSENCRYPT`: Set this to `True` if
  you are [using Let's Encrypt].  The default is `False`.  See the
  [`use lets encrypt`] configuration directive.
* <a name="LETSENCRYPTEMAIL"></a>`LETSENCRYPTEMAIL`: Set this to the
  e-mail address you use with [Let's Encrypt].  See the
  [`lets encrypt email`] configuration directive.
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
* <a name="POSTURLROOT"></a>`POSTURLROOT`: If users access
  **docassemble** at https://docassemble.example.com/da, set `URLROOT`
  to `/da/`.  The trailing slash is important.  If users access
  **docassemble** at https://docassemble.example.com, you can ignore
  this.  The default value is `/`.  See the [`root`] configuration
  directive.
* <a name="BEHINDHTTPSLOADBALANCER"></a>`BEHINDHTTPSLOADBALANCER`: Set
  this to `True` if a load balancer is in use and the load balancer
  accepts connections in HTTPS but forwards them to web servers as
  HTTP.  This lets **docassemble** know that when it forms URLs, it
  should use the `https` scheme even though requests appear to be
  coming in as HTTP requests.  See the [`behind https load balancer`]
  configuration directive.
* <a name="CROSSSITEDOMAIN"></a>`CROSSSITEDOMAIN`: If this is set, the
  [Apache] server will be configured to send a
  `Access-Control-Allow-Origin` header, which enables
  [Cross-Origin Resource Sharing].  Set this to `*` to allow sharing
  to any domain, or, e.g., `*.example.com` to limit sharing to a
  particular domain or subdomain.  See the [`cross site domain`]
  configuration directive.
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
  when the image is run.  See the [`debian packages`] configuration
  directive.
* <a name="PACKAGES"></a>`DASECRETKEY`: The secret key for protecting
  against cross-site forgery.  See the [`secret key`] configuration
  directive.  If `DASECRETKEY` is not set, a random secret key will be
  generated.

## Changing the configuration

If you already have an existing **docassemble** installation and you
want to `run` a new [Docker] container using it, but you want to
change the [configuration] of the container, there are some things you
will need to keep in mind.

The existing [configuration] file takes precedence over the
environment variables that you set using [Docker].
  
If you want to change the [configuration], and the server is running,
you can edit the [configuration] using the web interface.

If the server is not running, and you are using [persistent volumes],
you can use [`docker volume inspect`] to find the location of the
persistent volume, and find

When **docassemble** starts up on a [Docker] container, it:

* 
* Creates a [configuration] file from a template, using environment
  variables for initial values, if a [configuration] file does not
  already exist.
* Initializes a PostgreSQL database, if one is not already initialized.
* Configures the [Apache] configuration, if one is not already
  configured.
* Runs [Let's Encrypt] if the configuration indicates that
  [Let's Encrypt] should be used, and [Let's Encrypt] has not yet been
  configured.
  
When **docassemble** stops, it saves the [configuration] file, a
backup of the PostgreSQL database, and backups of the [Apache] and
[Let's Encrypt] configuration.  If you are using [persistent volumes],
the information will be stored there.  If you are using
[S3](#persistent s3) or [Azure blob storage](#persistent azure), the
information will be stored in the cloud.

When **docassemble** starts again, it will retrieve the
[configuration] file, the backup of the PostgreSQL database, and
backups of the [Apache] and [Let's Encrypt] configuration from storage
and use them for the container.

Suppose you have an existing installation that uses HTTPS and
[Let's Encrypt], but you want to change the [`DAHOSTNAME`].  The
[Apache] configuration files will not be overwritten if they already
exist when a new container starts up.  So if you had been using
[Let's Encrypt], but then you decide to change the [`DAHOSTNAME`], you
will need to delete the saved configuration before running a new
container.  If you are using [S3](#persistent s3), you can go to the
[S3 Console] and delete the "Apache" folder and the
"letsencrypt.tar.gz" file.  If you are using
[Azure blob storage](#persistent azure), you can go to the
[Azure Portal] and delete the "Apache" folder and the
"letsencrypt.tar.gz" file.
  
Also, if a configuration file exists on [S3](#persistent
s3)/[Azure blob storage](#persistent azure) (`config.yml`) or in a
[persistent volume], then the values in that configuration will take
precedence over the corresponding environment variables that are
passed to [Docker].  Once a configuration file exists, you should make
changes to the configuration file rather than passing environment
variables to [Docker].  However, if your configuration is on
[S3](#persistent s3)/[Azure blob storage](#persistent azure), you will
at least need to pass sufficient access keys (e.g., [`S3BUCKET`],
[`AZURECONTAINER`], etc.) to access that storage; otherwise your
container will not know where to find the configuration.

Also, there are some environment variables that do not exist in the
configuration file because they are specific to the individual server
being started.  These include the [`CONTAINERROLE`] and
[`SERVERHOSTNAME`] environment variables.

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
preferable solution, is to get an account on [Amazon Web Services]
([AWS]) or [Microsoft Azure].  If you use [AWS], create an [S3 bucket]
for your data, and then when you launch your container, set the
[`S3BUCKET`] and associated [environment variables].  If you use
[Microsoft Azure], create an [Azure blob storage] resource, and a
[blob storage container] within it, and then when you launch your
container, set the [`AZUREACCOUNTNAME`], [`AZUREACCOUNTKEY`], and
[`AZURECONTAINER`]<span></span> [environment variables].  When
[`docker stop`] is run, **docassemble** will backup the SQL database,
the [Redis] database, the [configuration], and your uploaded files to
your [S3 bucket] or [blob storage container].  Then, when you issue a
[`docker run`] command with [environment variables] pointing
**docassemble** to your [S3 bucket]/[Azure blob storage] resource,
**docassemble** will make restore from the backup.  You can
[`docker rm`] your container and your data will persist in the cloud.

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

## <a name="persistent azure"></a>Using Microsoft Azure

Using [Microsoft Azure] is very similar to using [S3].  From the
[Azure Portal] dashboard, search for "Storage accounts" in the
"Resources."  Click "Add" to create a new storage account.  Under
"Deployment model," choose
"Resource manager."  Under "Account kind," choose "Blob storage."
Under Performance, choose "Access tier," you can choose either "Cool"
or "Hot," but you may have to pay more for "Hot."

Once the storage account is created, go into it and click "+
Container" to add a new container.  Set the "Access type" to
"Private."  The name of the container corresponds with the
[`AZURECONTAINER`] environment variable.  Back at the storage account,
click "Access keys."  The "Storage account name" corresponds with the
environment variable [`AZUREACCOUNTNAME`].  The "key1" corresponds
with the [`AZUREACCOUNTKEY`] environment variable.  (You can also use
"key2.")

If you enable both [S3](#persistent s3) and
[Azure blob storage](#persistent azure), only [S3] will be used.

## <a name="persistent"></a>Using persistent volumes

To run **docassemble** in a [single-server arrangement] in such a way
that the [configuration], the [Playground] files, the uploaded files,
and other data persist after the [Docker] container is removed or
updated, run the image as follows:

{% highlight bash %}
docker run --env-file=env.list \
-v dabackup:/usr/share/docassemble/backup \
-d -p 80:80 -p 443:443 jhpyle/docassemble
{% endhighlight %}

where `--env-file=env.list` is an optional parameter that refers to a
file `env.list` containing environment variables for the
configuration.  A [template for the `env.list` file] is included in
distribution.

An advantage of using persistent volumes is that you can completely
replace the **docassemble** container and rebuild it from scratch, and
when you `run` the `jhpyle/docassemble` image again, docassemble will
keep running where it left off.

If you are using [HTTPS] with your own certificates (as opposed to
using [Let's Encrypt]), you can use a persistent volume to provide the
certificates to the [Docker] container.  Just add `-v
dacerts:/usr/share/docassemble/certs` to your [`docker run`] command.

To see what volumes exist on your [Docker] system, you can run:

{% highlight bash %}
docker volume ls
{% endhighlight %}

[Docker] volumes are actual directories on the file system.  To find
the path of a given volume, use [`docker volume inspect`]:

{% highlight bash %}
docker volume inspect dabackup
{% endhighlight %}

For example, if you are using [HTTPS] with your own certificates, and
you need to update the certificates your server should use, you can
find the path where the `dacerts` volume lives (`docker volume inspect
dacerts`), copy your certificates to that path (`cp mycertificate.key
/var/lib/docker/volumes/dacerts/data/docassemble.key`), and then stop
the container (`docker stop -t 60 <containerid>`) and start it again
(`docker start <containerid>`).

To delete all of the volumes, do:

{% highlight bash %}
docker volume rm $(docker volume ls -qf dangling=true)
{% endhighlight %}

Ultimately, the better [data storage] solution is to use cloud storage
([S3](#persistent s3), [Azure blob storage](#persistent azure)) because:

1. [S3](#persistent s3) and [Azure blob storage](#persistent azure)
   make scaling easier.  They are the "cloud" way of storing
   persistent data, at least until cloud-based network file systems
   become more robust.
2. It is easier to upgrade your virtual machines to the latest
   software and operating system if you can just destroy them and
   recreate them, rather than running update scripts.  If your
   persistent data is stored in the cloud, you can destroy and
   recreate virtual machines at will, without ever having to worry
   about copying your data on and off the machines.

# <a name="multi server arrangement"></a>Multi-server arrangement

## Services on different machines

The **docassemble** application consists of several services, some of
which are singular and some of which can be plural.

The singular services include:

* SQL
* [Redis]
* [RabbitMQ] for coordinating [background processes]
* The **docassemble** log message aggregator
* A [cron] service that runs [scheduled tasks] and housekeeping functions

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
For example, if you are already running a SQL server, a [Redis]
server, and a [RabbitMQ] server, you could just point **docassemble**
to those resources.

To change the SQL server that **docassemble** uses, edit the
[`DBHOST`], [`DBNAME`], [`DBUSER`], [`DBPASSWORD`], [`DBPREFIX`],
[`DBPORT`], and [`DBTABLEPREFIX`]<span></span> [configuration options].

To change the [Redis] server that **docassemble** uses, edit the
[`REDIS`]<span></span> [configuration option].

To change the [RabbitMQ] server that **docassemble** uses, edit the
[`RABBITMQ`]<span></span> [configuration option].

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
* If [`CONTAINERROLE`] includes `mail`: forward port 25 ([e-mails]).

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

Note that [Docker] will fail if any of these ports is already in use.
For example, many Linux distributions run a mail tranport agent on
port 25 by default; you will have to stop that service in order to
start [Docker] with `-p 25:25`.  For example, on [Amazon Linux] you
may need to run:

{% highlight bash %}
sudo /etc/init.d/sendmail stop
{% endhighlight %}

## <a name="file sharing"></a>File sharing

If you run multiple **docassemble** [Docker] containers on different
machines, the containers will need to have a way to share files with
one another.

One way to share files among containers is to make
`/usr/share/docassemble/` a [persistent volume] on a network file
system.  This directory contains the configuration, SSL certificates,
[Python virtual environment], and uploaded files.  However, network
file systems present problems.

A preferable way to share files is with [Amazon S3] or
[Azure blob storage], which **docassemble** supports.  See the
[using S3] and [using Azure blob storage] sections for instructions on
setting this up.

## Configuration file

Note that when you use the cloud ([S3](#persistent s3) or
[Azure blob storage](#persistent azure)) for [data storage],
**docassemble** will copy the `config.yml` file out of the cloud on
startup, and save `config.yml` to the cloud whenever the configuration
is modified.

This means that as long as there is a `config.yml` file in the cloud
with the configuration you want, you can start **docassemble**
containers without specifying a lot of [configuration options]; you
simply have to refer to your cloud storage bucket/container, and
**docassemble** will take it from there.  For example, to run a
central server, you can do:

{% highlight bash %}
docker run \
-e CONTAINERROLE=sql:redis:rabbitmq:log:cron:mail \
-e S3BUCKET=docassemble-example-com \
-e S3ACCESSKEY=FWIEJFIJIDGISEJFWOEF \
-e S3SECRETACCESSKEY=RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG \
-d -p 80:8080 -p 25:25 -p 5432:5432 -p 514:514 \
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

# <a name="Encryption"></a>Encrypting communications

## <a name="https"></a>Using HTTPS

If you are running **docassemble** on [EC2], the easiest way to enable
HTTPS support is to set up an [Application Load Balancer] that accepts
connections in HTTPS format and forwards them to the web servers in
HTTP format.  In this configuration [Amazon] takes care of creating
and hosting the necessary SSL certificates.

If you are not using a [load balancer], you can use HTTPS either by
setting up [Let's Encrypt] or by providing your own certificates.

### <a name="letsencrypt"></a>With Let's Encrypt

If you are running **docassemble** in a [single-server arrangement],
or in a [multi-server arrangement] with only one web server, you can
use [Let's Encrypt] to enable [HTTPS].  If you have more than one web
server, you can enable encryption [without Let's Encrypt] by
installing your own certificates.

To use [Let's Encrypt], set the following environment variables in
your task definition or `env.list` file:

* `USELETSENCRYPT`: set this to `True`.
* `LETSENCRYPTEMAIL`: [Let's Encrypt] requires an e-mail address, which
  it will use to get in touch with you about renewing the SSL certificates.
* `DAHOSTNAME`: set this to the hostname that users will use to get to
  the web application.  [Let's Encrypt] needs this in order to verify
  that you have access to the host.
* `USEHTTPS`: set this to `True`.

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

In addition, a [script] will run on a weekly basis to attempt to renew
the certificates.

If you are using a [multi-server arrangement] with a single web
server, you need to run the `cron` role on the same server that runs
the `web` role.  If you use the [e-mail receiving] feature with
[TLS encryption], the `mail` role also has to share the server with
the `web` and `cron` roles.

### <a name="without letsencrypt"></a>Without Let's Encrypt

Using your own SSL certificates with [Docker] requires that your SSL
certificates reside within each container.  There are several ways to
accomplish this:

* Use [S3](#persistent s3) or [Azure blob storage](#persistent azure)
  and upload the certificates to your bucket/container.
* [Build your own private image] in which your SSL certificates are
  placed in `Docker/apache.key`, `Docker/apache.crt`, and
  `Docker/apache.ca.pem`.  During the build process, these files
  will be copied into `/usr/share/docassemble/certs`.
* Use [persistent volumes] and copy the SSL certificate files
  (`apache.key`, `apache.crt`, and `apache.ca.pem`)
  into the volume for `/usr/share/docassemble/certs` before starting
  the container.

The default Apache configuration file expects SSL certificates to be
located in the following files:

{% highlight text %}
SSLCertificateFile /etc/ssl/docassemble/apache.crt
SSLCertificateKeyFile /etc/ssl/docassemble/apache.key 
SSLCertificateChainFile /etc/ssl/docassemble/apache.ca.pem
{% endhighlight %}

The meaning of these files is as follows:

* `apache.crt`: this file is generated by your certificate
  authority when you submit a certificate signing request.
* `apache.key`: this file is generated at the time you create
  your certificate signing request.
* `apache.ca.pem`: this file is generated by your certificate
  authority.  It is variously known as the "chain file"
  or the "root bundle."

In order to make sure that these files are replicated on every web
server, the [supervisor] will run the
`docassemble.webapp.install_certs` module before starting the web
server.

If you are using [S3](#persistent s3) or [Azure blob storage](#persistent azure), this module will copy
the files from the `certs/` prefix in your bucket/container to
`/etc/ssl/docassemble`.  You can use the [S3 Console] or the
[Azure Portal] to create a folder called `certs` and upload your
certificate files into that folder.

If you are not using [S3](#persistent s3) or [Azure blob storage](#persistent azure), the
`docassemble.webapp.install_certs` module will copy the files from
`/usr/share/docassemble/certs` to `/etc/ssl/docassemble`.

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

Note that the files need to be called `apache.crt`,
`apacke.key`, and `apache.ca.pem`, because this is what the
standard web server configuration expects.

If you want to use different filesystem or cloud locations, the
`docassemble.webapp.install_certs` can be configured to use different
locations.  See the [configuration] variables [`certs`] and
[`cert install directory`].

## <a name="tls"></a>Using TLS for incoming e-mail

If you use the [e-mail receiving] feature, you can use [TLS] to
encrypt incoming e-mail communications.  By default, **docassemble**
will install self-signed certificates into the [Exim] configuration,
but for best results you should use certificates that match your
[`incoming mail domain`].

If you are using [Let's Encrypt] to obtain your [HTTPS] certificates
in a [single-server arrangement], then **docassemble** will use your
[Let's Encrypt] certificates for [Exim].

However, if you are running your `mail` server as part of a dedicated
backend server that does not include `web`, you will need to create
and install your own certificates.  In addition, if your
[`incoming mail domain`] is different from your [`external hostname`]
([`DAHOSTNAME`]), then you will also need to install your own
certificates.

The process of installing your own [Exim] certificates is very similar to
the process of installing [HTTPS] certificates.

If you are using [S3](#persistent s3) or
[Azure blob storage](#persistent azure), copy your certificate and
private key to the `certs` folder of your [S3] bucket or
[Azure blob storage] container, using the filenames `exim.crt` and
`exim.key`, respectively.

If you are not using [S3](#persistent s3) or
[Azure blob storage](#persistent azure), save these files as:

* `/usr/share/docassemble/certs/exim.crt` (certificate)
* `/usr/share/docassemble/certs/exim.key` (private key)

On startup, `docassemble.webapp.install_certs` will copy these files
into the appropriate location (`/etc/exim4`) with the appropriate
ownership and permissions.

# <a name="forwarding"></a>Installing on a machine already using a web server

The simplest way to run **docassemble** is to give it a dedicated
machine and run [Docker] on ports 80 and 443.  However, if you have an
existing machine that is already running a web server, it is possible
to run **docassemble** on that machine using [Docker].  You can
configure the web server on that machine to forward traffic to the
[Docker] container.

The following example illustrates how to do this.  Your situation will
probably be different, but this example will still help you figure out
how to configure your system.

In this example, we will show how to run **docassemble** using
[Docker] on an Ubuntu 16.04 server.  The machine will run a web server
using encryption.  The web server will be accessible at
`https://justice.example.com` and will serve resources other than
**docassemble**.  The **docassemble** resources will be accessible at
`https://justice.example.com/da`.  [Docker] will run on the machine
and will listen on port 8080.  The web server will accept HTTPS
requests at `/da` and forward them HTTP requests to port 8080.  The
SSL certificate will be installed on the Ubuntu server, and the
[Docker] container will run an HTTP server.  [Docker] will be
controlled by the user account `ubuntu`, which is assumed to have
[sudo] privileges.

First, let's install [Apache], [Let's Encrypt] (the [certbot]
utility), and [Docker].  We log in to the server as `ubuntu` and do:

{% highlight bash %}
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get -y update
sudo apt-get -y install apache2 python-certbot-apache docker.io 
sudo usermod -a -G docker ubuntu
{% endhighlight %}

The last command changes the user privileges of the `ubuntu` user.
For these changes to take effect, we need to log out and log in again.
(E.g., exit the [ssh] session and start a new one.)

Before we run [certbot], let's add some basic information to the
[Apache] configuration.  Edit the standard HTTP configuration:

{% highlight bash %}
sudo vi /etc/apache2/sites-available/000-default.conf
{% endhighlight %}

and add the following lines, replacing any other lines that
begin with `ServerName` or `ServerAdmin`.

{% highlight text %}
ServerName justice.example.com
ServerAdmin admin@example.com
{% endhighlight %}

We then do the same with the HTTPS configuration.

{% highlight bash %}
sudo vi /etc/apache2/sites-available/default-ssl.conf
{% endhighlight %}

Now, let's enable some necessary components of [Apache]:

{% highlight bash %}
sudo a2ensite default-ssl
sudo a2enmod proxy_http
sudo a2enmod headers
sudo service apache2 reload
{% endhighlight %}

Then, we need to make sure that `justice.example.com` is directed to
this server.  This may require going to our DNS provider and adding a
[CNAME record] or an [A record].

We can test whether everything is working by going to
`http://justice.example.com` in a web browser.  We should see the
default [Apache] page.

Once that is done, we are ready to run [certbot].

{% highlight bash %}
sudo certbot --apache
{% endhighlight %}

When [certbot] asks "Please choose whether HTTPS access is required or
optional," we will select "Secure - Make all requests redirect to
secure HTTPS access."  This will cause all HTTP traffic to be
forwarded to HTTPS.

The [certbot] command will obtain certificates and modify the [Apache]
configuration.  A [cron] job will be installed that takes care of
renewing the certificates.

We can test whether the SSL certificates work by going to
`https://justice.example.com`.  We should see the default [Apache] page
again, but with encryption this time.

Now we are ready to run **docassemble**.  First we need to create a
short text file called `env.list` that contains some configuration
options for **docassemble**.

{% highlight bash %}
vi env.list
{% endhighlight %}

Set the contents of `env.list` to:

{% highlight text %}
BEHINDHTTPSLOADBALANCER=true
DAHOSTNAME=justice.example.com
URLROOT=https://justice.example.com
POSTURLROOT=/da/
{% endhighlight %}

The `POSTURLROOT` directive, which is set to `/da/`, indicates the
path after the domain at which **docassemble** can be accessed.  The
[Apache] web server will be able to provide other resources at other
paths, but `/da/` will be reserved for the exclusive use of
**docassemble**.  The beginning slash and the trailing slash are both
necessary.

Now, let's download, install, and run **docassemble**.

{% highlight bash %}
docker run --env-file=env.list -d -p 8080:80 jhpyle/docassemble
{% endhighlight %}

The option `-p 8080:80` means that port 8080 on the Ubuntu
machine will be mapped to port 80 within the [Docker] container.

Now that **docassemble** is running, let's configure [Apache] on the
Ubuntu machine to forward requests to **docassemble**.  Edit the HTTPS
configuration file:

{% highlight bash %}
sudo vi /etc/apache2/sites-available/default-ssl.conf
{% endhighlight %}

Add the following lines within the `<VirtualHost>` area:

{% highlight text %}
ProxyPass "/da"  "http://localhost:8080/da"
ProxyPassReverse "/da"  "http://localhost:8080/da"
RequestHeader set X-Forwarded-Proto "https"
{% endhighlight %}

Then restart the web server:

{% highlight bash %}
sudo service apache2 restart
{% endhighlight %}

Now, when we go to `https://justice.example.com/da`, we will see the
**docassemble** demo interview.

# <a name="build"></a>Creating your own Docker image

To create your own [Docker] image, first make sure [git] is installed:

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

* <span></span>[`docassemble/Dockerfile`]: you may want to change the
  locale and the Debian mirror; the standard "httpredir" mirror can
  lead to random packages not being downloaded, depending on which
  mirrors it chooses to use.
* <span></span>[`docassemble/Docker/config/config.yml.dist`]: you
  probably do not need to change this; it is a template that is
  updated based on the contents of the environment variables passed to
  [`docker run`].  Once your server is up and running you can change
  the rest of the configuration in the web application.
* <span></span>[`docassemble/Docker/initialize.sh`]: this script
  updates `config.yml` based on the environment variables; retrieves a
  new version of `config.yml` from [S3]/[Azure blob storage], if
  available; if [`CONTAINERROLE`] is not set to `web`, starts the
  [PostgreSQL] server and initializes the database if it does not
  exist; creates the tables in the database if they do not already
  exist; copies SSL certificates from [S3]/[Azure blob storage] or
  `/usr/share/docassemble/certs` if [S3]/[Azure blob storage] is not
  enabled; enables the [Apache] `mod_ssl` if `USEHTTPS` is `True` and
  otherwise disables it; runs the [Let's Encrypt] utility if
  `USELETSENCRYPT` is `True` and the utility has not been run yet; and
  starts [Apache] and other background tasks.
* <span></span>[`docassemble/Docker/config/docassemble-http.conf.dist`]:
  [Apache] configuration file for handling HTTP requests.
  Note that if `mod_ssl` is enabled, HTTP will merely redirect to
  HTTPS.
* <span></span>[`docassemble/Docker/config/docassemble-ssl.conf.dist`]:
  [Apache] configuration file for handling HTTPS requests.
* <span></span>[`docassemble/Docker/config/docassemble-log.conf.dist`]:
  [Apache] configuration file for handling requests on port 8080.
  This is enabled if the [`CONTAINERROLE`] includes `log`.
* <span></span>[`docassemble/Docker/ssl/apache.crt.orig`]: default SSL certificate for [Apache].
* <span></span>[`docassemble/Docker/ssl/apache.key.orig`]: default SSL certificate for [Apache].
* <span></span>[`docassemble/Docker/ssl/apache.ca.pem.orig`]: default SSL certificate for [Apache].
* <span></span>[`docassemble/Docker/ssl/exim.crt.orig`]: default SSL certificate for [Exim].
* <span></span>[`docassemble/Docker/ssl/exim.key.orig`]: default SSL certificate for [Exim].
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
* <span></span>[`docassemble/Docker/docassemble.logrotate`]: This file will be copied
  into `/etc/logrotate.d` and will control the rotation of the
  **docassemble** log file in `/usr/share/docassemble/log`.
* <span></span>[`docassemble/Docker/apache.logrotate`]: This replaces the standard
  apache logrotate configuration.  It does not compress old log files,
  so that it is easier to view them in the web application.
* <span></span>[`docassemble/Docker/process-email.sh`]: This is a
  script that is run when an e-mail is received, if the
  [e-mail receiving] feature is configured.
* <span></span>[`docassemble/Docker/run-apache.sh`]: This is a script
  that is run by [supervisor] to start the [Apache] server.
* <span></span>[`docassemble/Docker/run-celery.sh`]: This is a script
  that is run by [supervisor] to start the [Celery] server.
* <span></span>[`docassemble/Docker/run-cron.sh`]: This is a script
  that is run by [supervisor] to start the [cron] daemon.
* <span></span>[`docassemble/Docker/run-postgresql.sh`]: This is a script that is
  run by [supervisor] to start the [PostgreSQL] server.
* <span></span>[`docassemble/Docker/run-rabbitmq.sh`]: This is a script that is
  run by [supervisor] to start the [RabbitMQ] server.
* <span></span>[`docassemble/Docker/run-redis.sh`]: This is a script that is
  run by [supervisor] to start the [Redis] server.
* <span></span>[`docassemble/Docker/run-syslogng.sh`]: This is a script that is
  run by [supervisor] to start the [Syslog-ng] daemon.
* <span></span>[`docassemble/Docker/run-websockets.sh`]: This is a script that is
  run by [supervisor] to start the [WebSocket] server.
* <span></span>[`docassemble/Docker/reset.sh`]: This is a script that is
  run by [supervisor] to restart the web server, the [Celery] server,
  and the [WebSocket] server on a signal from a peer server.
* <span></span>[`docassemble/Docker/sync.sh`]: This is a script that is
  run by [supervisor] to synchronize log files.
* <span></span>[`docassemble/Docker/update.sh`]: This is a script that is
  run by [supervisor] to update the software on the container.

To build the image, run:

{% highlight bash %}
cd docassemble
docker build -t yourdockerhubusername/mydocassemble .
{% endhighlight %}

You can then run your image:

{% highlight bash %}
docker run -d -p 80:80 -p 443:443 -p 25:25 -p 9001:9001 yourdockerhubusername/mydocassemble
{% endhighlight %}

Or push it to [Docker Hub]:

{% highlight bash %}
docker push yourdockerhubusername/mydocassemble
{% endhighlight %}

# Upgrading docassemble when using Docker

As new versions of **docassemble** become available, you can obtain
the latest version by running this within the "docassemble" directory:

{% highlight bash %}
docker pull jhpyle/docassemble
{% endhighlight %}

Then, subsequent [`docker run`] commands will use the latest
**docassemble** image.

When you are using [Docker] to run **docassemble**, you can upgrade
**docassemble** to the newest version simply by running `docker pull
jhpyle/docassemble`, then running [`docker stop`] and [`docker rm`] on
your **docassemble** container, followed by [`docker run`].  Note,
however, that [`docker rm`] will delete all of the data on the server
unless you are using a [data storage] system.

# Cleaning up after Docker

If you run `docker pull` to retrieve new versions of **docassemble**,
or you build your own **docassemble** images more than once, you may
find your disk space being used up.  The full **docassemble** image is
about 4GB in size, and whenever you run `docker pull` or build a new
image, a new image is created -- the old image is not overwritten.

The following three lines will stop all containers, remove all
containers, and then remove all of the images that [Docker] created
during the build process.

{% highlight bash %}
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images | grep "^<none>" | awk "{print $3}")
{% endhighlight %}

The last line, which deletes images, frees up the most disk space.
However, it may be necessary to remove the containers first, as the
containers depend on the images.

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
[using HTTPS]: #https
[docassemble repository]: {{ site.github.repository_url }}
[`docassemble/Dockerfile`]: {{ site.github.repository_url }}/blob/master/Dockerfile
[`docassemble/Docker/config/config.yml.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/config.yml.dist
[`docassemble/Docker/initialize.sh`]: {{ site.github.repository_url }}/blob/master/Docker/initialize.sh
[`docassemble/Docker/config/docassemble-http.conf.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/docassemble-http.conf.dist
[`docassemble/Docker/config/docassemble-ssl.conf.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/docassemble-ssl.conf.dist
[`docassemble/Docker/config/docassemble-log.conf.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/docassemble-log.conf.dist
[`docassemble/Docker/ssl/apache.crt.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/apache.crt.orig
[`docassemble/Docker/ssl/apache.key.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/apache.key.orig
[`docassemble/Docker/ssl/apache.ca.pem.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/apache.ca.pem.orig
[`docassemble/Docker/ssl/exim.crt.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/exim.crt.orig
[`docassemble/Docker/ssl/exim.key.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/exim.key.orig
[`docassemble/Docker/docassemble.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.conf
[`docassemble/Docker/docassemble-supervisor.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble-supervisor.conf
[`docassemble/Docker/docassemble-syslog-ng.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble-syslog-ng.conf
[`docassemble/Docker/syslog-ng.conf`]: {{ site.github.repository_url }}/blob/master/Docker/syslog-ng.conf
[`docassemble/Docker/rabbitmq.config`]: {{ site.github.repository_url }}/blob/master/Docker/rabbitmq.config
[`docassemble/Docker/docassemble.logrotate`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.logrotate
[`docassemble/Docker/apache.logrotate`]: {{ site.github.repository_url }}/blob/master/Docker/apache.logrotate
[`docassemble/Docker/process-email.sh`]: {{ site.github.repository_url }}/blob/master/Docker/process-email.sh
[`docassemble/Docker/run-postgresql.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-postgresql.sh
[`docassemble/Docker/run-apache.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-apache.sh
[`docassemble/Docker/run-celery.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-celery.sh
[`docassemble/Docker/run-cron.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-cron.sh
[`docassemble/Docker/run-rabbitmq.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-rabbitmq.sh
[`docassemble/Docker/run-redis.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-redis.sh
[`docassemble/Docker/run-syslogng.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-syslogng.sh
[`docassemble/Docker/run-websockets.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-websockets.sh
[`docassemble/Docker/reset.sh`]: {{ site.github.repository_url }}/blob/master/Docker/reset.sh
[`docassemble/Docker/sync.sh`]: {{ site.github.repository_url }}/blob/master/Docker/sync.sh
[`docassemble/Docker/update.sh`]: {{ site.github.repository_url }}/blob/master/Docker/update.sh
[template for the `env.list` file]: {{ site.github.repository_url }}/blob/master/Docker/env.list
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
[`azure` section]: {{ site.baseurl }}/docs/config.html#azure
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
[`cert install directory`]: {{ site.baseurl }}/docs/config.html#cert install directory
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
[`AZURECONTAINER`]: #AZURECONTAINER
[`AZUREACCOUNTNAME`]: #AZUREACCOUNTNAME
[`AZUREACCOUNTKEY`]: #AZUREACCOUNTKEY
[`CONTAINERROLE`]: #CONTAINERROLE
[`SERVERHOSTNAME`]: #SERVERHOSTNAME
[`DAHOSTNAME`]: #DAHOSTNAME
[`USEHTTPS`]: #USEHTTPS
[`USELETSENCRYPT`]: #USELETSENCRYPT
[Celery]: http://www.celeryproject.org/
[background processes]: {{ site.baseurl }}/docs/background.html#background
[Windows PowerShell]: https://en.wikipedia.org/wiki/PowerShell
[Terminal]: https://en.wikipedia.org/wiki/Terminal_(macOS)
[`timezone`]: {{ site.baseurl }}/docs/config.html#timezone
[`os locale`]: {{ site.baseurl }}/docs/config.html#os locale
[`other os locales`]: {{ site.baseurl }}/docs/config.html#other os locales
[`behind https load balancer`]: {{ site.baseurl }}/docs/config.html#behind https load balancer
[`rabbitmq`]: {{ site.baseurl }}/docs/config.html#rabbitmq
[`redis`]: {{ site.baseurl }}/docs/config.html#redis
[`log server`]: {{ site.baseurl }}/docs/config.html#log server
[`lets encrypt email`]: {{ site.baseurl }}/docs/config.html#lets encrypt email
[`use lets encrypt`]: {{ site.baseurl }}/docs/config.html#use lets encrypt
[`external hostname`]: {{ site.baseurl }}/docs/config.html#external hostname
[`use https`]: {{ site.baseurl }}/docs/config.html#use https
[`ec2`]: {{ site.baseurl }}/docs/config.html#ec2
[`debian packages`]: {{ site.baseurl }}/docs/config.html#debian packages
[`url root`]: {{ site.baseurl }}/docs/config.html#url root
[`root`]: {{ site.baseurl }}/docs/config.html#root
[Debian]: https://www.debian.org/
[using S3]: #persistent s3
[using Azure blob storage]: #persistent azure
[environment variables]: #configuration options
[GitHub]: https://github.com
[data storage]: #data storage
[`docker stop`]: https://docs.docker.com/engine/reference/commandline/stop/
[`docker rm`]: https://docs.docker.com/engine/reference/commandline/rm/
[`docker run`]: https://docs.docker.com/engine/reference/commandline/run/
[`docker build`]: https://docs.docker.com/engine/reference/commandline/build/
[`docker ps`]: https://docs.docker.com/engine/reference/commandline/ps/
[`docker volume`]: https://docs.docker.com/engine/reference/commandline/volume/
[`docker volume inspect`]: https://docs.docker.com/engine/reference/commandline/volume_inspect/
[Amazon Web Services]: https://aws.amazon.com
[AWS]: https://aws.amazon.com
[S3 bucket]: http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
[scheduled tasks]: {{ site.baseurl }}/docs/background.html#scheduled
[WebSocket]: https://en.wikipedia.org/wiki/WebSocket
[e-mails]: {{ site.baseurl }}/docs/background.html#email
[e-mail receiving]: {{ site.baseurl }}/docs/background.html#email
[Exim]: https://en.wikipedia.org/wiki/Exim
[TLS]: https://en.wikipedia.org/wiki/Transport_Layer_Security
[`incoming mail domain`]: {{ site.baseurl }}/docs/config.html#incoming mail domain
[git]: https://en.wikipedia.org/wiki/Git
[without Let's Encrypt]: #without letsencrypt
[script]: {{ site.github.repository_url }}/blob/master/Docker/cron/docassemble-cron-weekly.sh
[TLS encryption]: #tls
[Azure Portal]: https://portal.azure.com/
[Azure blob storage]: https://azure.microsoft.com/en-us/services/storage/blobs/
[Microsoft Azure]: https://azure.microsoft.com/
[blob storage container]: https://docs.microsoft.com/en-us/azure/storage/storage-dotnet-how-to-use-blobs#create-a-container
[certbot]: https://certbot.eff.org/
[sudo]: https://en.wikipedia.org/wiki/Sudo
[ssh]: https://en.wikipedia.org/wiki/Secure_Shell
[CNAME record]: https://en.wikipedia.org/wiki/CNAME_record
[A record]: https://en.wikipedia.org/wiki/List_of_DNS_record_types#A
[Security Group]: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html
[HTTP]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
[region]: http://docs.aws.amazon.com/general/latest/gr/rande.html
[`secret key`]: {{ site.baseurl }}/docs/config.html#secret key
[Cross-Origin Resource Sharing]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[`cross site domain`]: {{ site.baseurl }}/docs/config.html#cross site domain
