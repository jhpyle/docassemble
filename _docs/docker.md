---
layout: docs
title: Installing on Docker
short_title: Docker
---

[Docker] is an application that treats a whole Linux machine,
including its operating system and installed applications, as a
computer-within-a-computer, called a "container."  "Containers" are
similar to a [virtual machine] in many respects. They are typically
used for "shipping" applications. Instead of installing an
application on a server directly, you can run the application in a
"container."  This way, the application runs bundled with all of the
operating system software that it needs. Installing applications is
quicker, simpler, and less error-prone. There is virtually no
performance degredation.

[Docker] is a good platform for trying out **docassemble** for the
first time. It is also ideal in a production environment.

Since the **docassemble** application depends on so many different
component parts, including a web server, SQL server, Redis server,
distributed task queue, background task system, scheduled task system,
and other components, running it inside of a [Docker] container is
convenient. When all of these components are running inside of a
"container," you don't have to do the work of installing and
maintaining these components.

[Docker] can also be used to deploy even the most complex
**docassemble** installations. For example, [Kubernetes] or Amazon's
[EC2 Container Service] can be used to maintain a cluster of
**docassemble** web server instances, created from [Docker] images,
that communicate with a central server. For information about how to
install **docassemble** in a multi-server arrangement, see the
[scalability] section.

As much as [Docker] simplifies the process of installing
**docassemble**, it takes some time to understand the concepts behind
"running," "stopping," and "starting" containers. [Docker] is a
complex and powerful tool, and the **docassemble** documentation is
not a substitute for [Docker] documentation. If you are new to
[Docker], you should learn about [Docker] by reading tutorials or
watching videos. The documentation on this page assumes you are using
the [Docker] command line interface, so it is recommended you learn
about that, rather than graphical interfaces or "container management"
systems that gloss over important details.

Here is a brief cheat sheet guide to the [Docker] commands, based on
loose real-world analogies:

* Doing [`docker run`] is analogous to getting a Windows
  installation DVD, installing it on a computer with an empty hard
  drive, and then booting the computer for the first time.
* Doing [`docker pull`] is analogous to going to a store and obtaining
  a Windows installation DVD.
* Doing [`docker stop`] is analogous to clicking "shut down" from the
  Windows "start" menu, waiting a certain number of seconds, and then
  unplugging the computer if it hasn't turned off yet.
* Doing [`docker kill`] is analogous to unplugging your Windows
  computer while it is on, without clicking "shut down" from the
  Windows "start" menu.
* Doing [`docker start`] is analogous to turning on a computer that
  already has Windows installed on it.
* Doing [`docker exec`] is analogous to sitting down at your Windows
  computer and opening up PowerShell.
* Doing [`docker ps`] is analogous to walking around your house and
  making a list of your computers.
* Doing [`docker images`] is analogous to walking around your house and
  making a list of your Windows installation DVDs.
* Doing [`docker rm`] is analogous to tossing a computer into a
  trash incinerator.
* Doing [`docker rmi`] is analogous to tossing a Windows installation
  DVD into a trash incinerator.
* Doing [`docker volume`] is analogous to doing things with USB drives.
* Doing [`docker build`] is analogous to creating a Windows
  installation DVD based on the Windows source code.
* Doing [`docker commit`] is analogous to creating a Windows
  installation DVD based on the the current state of your
  Windows PC.
* Doing [`docker save`] is analogous to taking a Windows installation
  DVD out of your house and into your car.
* Doing [`docker load`] is analogous to taking a Windows
  installation DVD out of your car and into your house.

In these analogies, a [Docker] "image" is analogous to a Windows
installation DVD, a [Docker] "container" is analogous to a particular
computer that runs Windows, and a [Docker] "volume" is (very loosely)
analogous to a USB drive.

# <a name="where"></a>Choosing where to run Docker

[Docker] can be run on a Windows PC, a Mac, an on-site Linux machine,
or a Linux-based virtual machine in the cloud. Since **docassemble**
is a web application, the ideal platform is a Linux virtual machine in
the cloud.

You can test out **docassemble** on a PC or a Mac, but for serious,
long-term deployment, it is worthwhile to run it in the cloud, or on a
dedicated on-premises server. Running [Docker] on a machine that shuts
down or restarts frequently could lead to [database corruption]. Also,
if you are using [Docker Desktop], **docassemble** may not run
reliably if you have a processor that is not in the `amd64` family.

If you have never deployed a Linux-based virtual machine in the cloud
before, this might be a good opportunity to learn. The ability to use
virtual machines on a cloud provider like [Amazon Web Services] or
[Microsoft Azure] is a valuable and transferable skill. Learning how
to do cloud computing is beyond the scope of this documentation, but
there are many guides on the internet. The basic steps of running
Docker in the cloud are:

1. Create an account with a cloud computing provider.
2. Start a [sufficiently powerful](#install) virtual machine that runs
   some flavor of Linux.
3. In the networking configuration (sometimes called the "firewall" or
   "security group"), open up ports 80 (HTTP) and 443 (HTTPS) to the
   outside world.
4. Connect to the virtual machine using [SSH] in order to control it
   using a command line. This can be a complicated step because most
   providers use certificates rather than passwords for
   authentication. This requires port 22 to be open to the outside
   world. Some cloud providers may give you the option of connecting
   to a console from within the web browser.
5. [Install Docker](#install) on the virtual machine.

See the [example deployment] for step-by-step instructions using
[Amazon Lightsail].

There are also methods of controlling cloud computing resources from a
local command line (for example, the [AWS CLI] and the [Azure CLI]),
where you type special commands to deploy [Docker] containers. These
can be very useful, but they tend to be more complicated to use than
the basic [Docker] command line.

# <a name="install"></a>Installing Docker

First, make sure you are running [Docker] on a computer or virtual
computer with at least 4GB of memory and 40GB of hard drive space.
The **docassemble** installation will use up about 20GB of space, and
you should always have at least 20GB free when you are running
**docassemble**.

If you have a Windows PC, follow the
[Docker installation instructions for Windows]{:target="_blank"}. You
will need administrator access on your PC in order to install (or
upgrade) Docker.

If you have a Mac, follow the [Docker installation instructions for OS X]{:target="_blank"}.

On Ubuntu (assuming username `ubuntu`):

{% highlight bash %}
sudo apt -y update
sudo apt -y install docker.io
sudo usermod -a -G docker ubuntu
{% endhighlight %}

On [Amazon Linux] (assuming the username `ec2-user`):

{% highlight bash %}
sudo yum -y update
sudo yum -y install docker
sudo usermod -a -G docker ec2-user
{% endhighlight %}

The `usermod` line allows the non-root user to run [Docker]. You may
need to log out and log back in again for this new user permission to
take effect. On some distributions, the `docker` group is not created
by the installation process, so you will need to manually create it by
running `sudo groupadd docker` before you run the `usermod` command.

[Docker] may or may not start automatically after it is installed. On
Linux, you many need to do `sudo systemctl start docker`, `sudo
service docker start`, or `sudo /etc/init.d/docker start`.

The operating system that runs inside of the **docassemble** Docker
container is Ubuntu 24.04. This is a fairly recent version of
Ubuntu. When using [Docker], it is recommended that you run a recent
version of [Docker] and its dependencies ([containerd] and
[runC]). Ubuntu 22 and Debian 12 are known to work well. (If you run
Docker on Mac or Windows, it will likely start a virtual machine and
then deploy the **docassemble** Docker container inside that virtual
machine; the operating system of that virtual machine, which is likely
a flavor of Linux, should be recent.)  You may encounter
difficult-to-diagnose problems if **docassemble**'s OS and software do
not fully function inside the host operating system. It is difficult
to predict what these errors will be. If you run the latest
**docassemble** image on an OS that is older than Ubuntu 22, it is
likely that you will encounter problems, if not right away then at a
later point in time. The software in the **docassemble** image and
Python packages is continually updated, and the latest versions of
software may expect the latest versions of operating system.

As of August 2024, Ubuntu 24.04's `docker.io` package has a problem
with AppArmor interfering with the functionality of [`docker
stop`]. If you use Ubuntu 24.04 as the operating system on which to
run Docker, follow the instructions on Docker's web site for
installing the Community Edition.

If you are using [Docker Desktop], it is recommended that you go to
Settings and change the Docker Engine settings so that the
`shutdown-timeout` is at least 600 seconds. Otherwise, Docker Desktop
may forcibly terminate your **docassemble** container while it is
trying to safely shut down.

{% highlight javascript %}
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "shutdown-timeout": 600
}
{% endhighlight %}

# <a name="single server arrangement"></a>Quick start

If you just want to test out **docassemble** for the first time,
follow the instructions in this section, and you'll get
**docassemble** up and running quickly in a [Docker] container,
whether you are using a laptop or [AWS].

However, you should think of this as an educational exercise; don't
start using the container for serious development work. For a serious
implementation, you should deploy **docassemble** on a server (in the
cloud or on-premises), and go through additional setup steps, such as
configuring [HTTPS] for encryption and [data storage] for the safe,
long-term storage of development data and user data.

## <a name="starting"></a>Starting

Once [Docker] is installed, you can install and run **docassemble** from the command line.

To get a command line on Windows, run [Windows PowerShell].

To get a command line on a Mac, launch the [Terminal] application.

To get a command line on a virtual machine in the cloud, follow your
provider's instructions for using [SSH] to connect to your machine.

From the command line, simply type in:

{% highlight bash %}
docker run -d -p 80:80 -p 443:443 --restart always --stop-timeout 600 jhpyle/docassemble
{% endhighlight %}

The [`docker run`] command will download and run **docassemble**,
making the application available on the standard HTTP port (port 80)
of your machine.

In the [`docker run`] command, the `-d` flag means that the container
will run in the background.

The `-p` flag maps a port on the host machine to a port on the
[Docker] container. In this example, port 80 on the host machine will
map to port 80 within the [Docker] container. If you are already
using port 80 on the host machine, you could use `-p 8080:80`, and
then port 8080 on the host machine would be passed through to port 80
on the [Docker] container.

The `jhpyle/docassemble` tag refers to a [Docker] image that is
[hosted on Docker Hub]. The image is about 4GB in size, and when it
runs, the container uses about 10GB of hard drive space. The
`jhpyle/docassemble` image is based on the "master" branch of the
[docassemble repository] on [GitHub]. It is rebuilt every time the
minor version of **docassemble** increases.

If you are using the graphical user interface of [Docker Desktop] to
start a container using the `jhpyle/docassemble` image, then [Docker
Desktop] will run `docker run` for you, and you will not be able to
specify the command line parameters directly. Under the "optional
settings," make sure to map port 80 to port 80 (the equivalent of `-p
80:80`). If it doesn't let you do that, try mapping port `8080` to
port `80`, in which case **docassemble** will be available at
`http://localhost:8080`.

It will take several minutes for **docassemble** to download, and once
the [`docker run`] command finishes, **docassemble** will start to
run. After a few minutes, you can point your web browser to the
hostname of the machine that is running [Docker]. If you are running
[Docker] on your own computer, this address is probably
http://localhost.

Note that the **docassemble** web interface is not available
immediately after the `docker run` finishes. The server needs time to
boot and initialize. On [EC2], this process takes about one minute
forty seconds, and it might be slower on other platforms. If you want
to investigate what is happening on the server, see the
[troubleshooting] section. (If you have an existing configuration in
[data storage], the boot process will take even longer because your
software and databases will need to be copied from [data storage] and
restored on the server).

If you are running [Docker] on [AWS], the address of the server will
be something like
`http://ec2-52-38-111-32.us-west-2.compute.amazonaws.com` (check your
[EC2] configuration for the hostname). On [AWS], you will need a
[Security Group] that opens [HTTP] (port 80) to the outside world in
order to allow web browsers to connect to your [EC2] instance.

Using the web browser, you can log in using the default username
("admin@example.com") and password ("password"), and make changes to the
configuration from the menu. You should go to User List from the menu,
click "Edit" next to the `admin@example.com` user, and change that
e-mail address to an actual e-mail address you can access.

## <a name="shutdown"></a>Shutting down

You can shut down the container by running:

{% highlight bash %}
docker stop -t 600 <containerid>
{% endhighlight %}

By default, [Docker] gives containers ten seconds to shut down before
forcibly shutting them down. Ten seconds may be enough time in some
situations, but you should assume that **docassemble** might need
longer than ten seconds to shut down. To be safe, give the container
plenty of time to shut down gracefully. The `-t 600` switch means that
[Docker] will wait up to ten minutes (600 seconds) before forcibly
shutting down the container.

It is very important to avoid a forced shutdown of **docassemble**.
The container uses a [PostgreSQL] server running internally (unless
configured to use an external SQL server), and the data files of the
server may become corrupted if [PostgreSQL] is not gracefully shut
down. To facilitate [data storage] (more on this later),
**docassemble** backs up your data during the shutdown process and
restores from that backup during the startup process. If the shutdown
process is interrupted, your data may be left in an inconsistent
state. As a safety measure, if the **docassemble** startup process
detects that the previous shutdown process was interrupted, it will
not attempt to restore data from [data storage], and it will resume
using the working files it had been using before the last shutdown.

To see a list of stopped containers, run `docker ps -a`. To remove a
container, run `docker rm <containerid>`.

## <a name="starting after shutdown"></a>Restarting the container after a shutdown

If you have shut down a [Docker] container using [`docker stop -t 600`],
you can start the container again:

{% highlight bash %}
docker start <containerid>
{% endhighlight %}

# <a name="overview"></a>Overview of the Docker container

There are a variety of ways to deploy **docassemble** with [Docker],
but this subsection will give an overview of the most common way,
which is to use a single [Docker] container hosted on a cloud
provider.

When you run [`docker run`] on the "image" `jhpyle/docassemble`,
[Docker] will go onto the internet, download ("pull") the
`jhpyle/docassemble` image, create a new container using that image,
and then "start" that container. However, first it will check to see
if a copy of the `jhpyle/docassemble` image has already been
downloaded, and if there is a copy already downloaded, it will create
the container using that copy. This is important to keep in mind;
when you run `docker run`, you might be thinking you will always get
the most recent version, but that is not the case. (See [upgrading],
below, for more information.)

When the **docassemble** container starts, it runs one command:

{% highlight bash %}
/usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
{% endhighlight %}

(This is specified in the [`Dockerfile`], if you are curious.)

This command starts an application called [Supervisor]. [Supervisor]
is a "process control system" that starts up the various applications
that **docassemble** uses, including:

* A web server, [NGINX], which is called `nginx` within the Supervisor
  configuration.
* An application server, [uWSGI], called `uwsgi`.
* A [background task] system, [Celery], consisting of two processes,
  `celery` and `celerysingle`.
* A scheduled task runner, called `cron`, which supports the
  [scheduled tasks] feature and [deletes inactive sessions].
* A server for [receiving emails], called `exim4`.
* A SQL server, [PostgreSQL], called `postgres`, which stores user
  account information, interview answers, and other application data
  (which will not be used if the [`db`] Configuration points to an
  external server).
* A distributed task queue system, [RabbitMQ], called `rabbitmq`,
  which supports the [Celery]-based [background process] system.
* An in-memory data structure store, [Redis], called `redis` (which
  will not be used if the [`redis`] Configuration points to an
  external server).
* A watchdog daemon that looks for out-of-control processes and
  kills them, called `watchdog`.
* A [WebSocket] server that supports the [live help] functionality,
  called `websockets`.
* A [unoconv] server, called `unoconv` (which will be used for DOCX to
  PDF conversion if [`enable unoconv`] is true).

In addition to starting background tasks, [Supervisor] coordinates the
running of ad-hoc tasks, including:

* A bare-bones web server called `nascent` that runs during the
  initialization process, so that the application responds on port 80
  while the initialization process is happening. As soon as the
  initialization process finishes, the `nascent` task is stopped and
  the `nginx` task is started.
* A script called `sync` that consolidates log files in one place,
  to support the [Logs] interface. This is run when you visit the Logs
  page in the web interface.
* A script called `update` that installs and upgrades the [Python]
  packages on the system. This is run when you use the Package
  Management page in the web interface.
* A script called `reset` that restarts each of the tasks that use the
  **docassemble** [Python] packages. This is called after packages are
  installed, [Python] modules are changed, or the [Configuration] is
  changed.

There is also a [Supervisor] service called `syslogng`, which is
dormant on a single-server system. (The [syslog-ng] application is
used in the multi-server arrangement to consolidate log files from
multiple machines.)

For the web server, [NGINX] is used by default, but it is possible
(mostly for backwards compatibility reasons) to run Apache instead of
[NGINX]. For this reason, there is a service called `apache2`, which
is defined in the configuration but does not run unless `DAWEBSERVER`
is set to `apache`.

Finally, there is a service called `initialize`, which runs
automatically when [Supervisor] starts. This is a shell script that
initializes the server and starts the other services in the correct
order.

## <a name="initialize"></a>What happens during startup

When `supervisord` starts, the `watchdog`, `nascent` and `initialize`
processes are started. The `initialize` process is a `bash` script,
`/usr/share/docassemble/webapp/initialize.sh`, that performs
initialization tasks and calls `supervisorctl` to start other tasks
that `supervisord` will manage.

The `initialize` script does the following.

* The script detects if there was an unsafe shutdown; if there was an
  unsafe shutdown, then the commands that restore application data
  from [data storage] will not be run.
* The `apt-get update` command is run so that the container can run
  `apt-get install` commands later in the process.
* If S3 is enabled, the bucket will be created if it does not already
  exist.
* If data for an existing server is available in data storage, files
  are copied from data storage to working directories. This includes:
    * Let's Encrypt files (`letsencrypt.tar.gz` is unpacked into
      `/etc/letsencrypt`);
    * Log files (`/var/log/nginx` and `/usr/share/docassemble/log`);
    * The configuration file (`config.yml` is copied to
      `/usr/share/docassemble/config/config.yml`); and
    * The [Redis] database (`redis.rdb` is copied to
      `/var/lib/redis/dump.rdb`).
* If `/usr/share/docassemble/config/config.yml` does not exist, a
  configuration file is created based on default values, a
  randomly-generated `secretkey`, and [Docker] environment
  variables.
* The `config.yml` file is read and environment variables are set
  based on the values in the `config.yml` file. (Some of the
  initialization commands that run in the `bash` script rely on
  environment variables.)
* The script detects whether this container is starting up for the
  first time; that is, whether a [`docker run`] or [`docker start`] is
  happening.
* If a [`docker run`] is happening, the file permissions are changed
  to allow the `www-data` user to make changes to Python packages and
  the Configuration. However, if the environment variables indicate
  that these files should not be modifiable by the `www-data` user,
  this step is skipped.
* The [NGINX] base configuration files are created based on the
  Configuration.
* If [S3] or [Azure Blob Storage] is being used, the Configuration is
  saved to the cloud.
* If [S3] or [Azure Blob Storage] is being used, and there is no
  `files` folder in the cloud, but there is a local directory
  `/usr/share/docassemble/files`, that directory is copied to the
  `files` folder in [S3].
* The [NGINX] site configuration files are created based on the
  Configuration and Let's Encrypt data.
* The `/etc/locale.gen` file is updated and the `update-locale` and
  `locale-gen` utilities are run based on the [`os locale`] specified in
  the Configuration.
* Ubuntu packages specified in the [`ubuntu packages`] Configuration
  directive are installed with `apt-get`.
* If a `pip index url` is specified in the Configuration, then `pip
  config` is run to set the `pip` global index.
* The Python packages specified in `python packages` are installed.
* The time zone specified in the `timezone` Configuration directive is
  configured in the operating system.
* If custom HTTPS certificates are used, they are copied from
  `/usr/share/docassemble/certs` into their working directories.
* The local PostgreSQL database is started.
    * The PostgreSQL process is started using `supervisorctl`.
    * The script waits until PostgreSQL is ready.
    * If the PostgreSQL role indicated by the `user` directive under
      `db` does not exist, it is created.
    * Any PostgreSQL database dump files that exist in data storage
      (under `postgres`) are restored using `pg_restore -F c -C -c`.
    * If the PostgreSQL database indicated by the `name` directive
      under `db` does not exist, it is created, and ownership is given
      to the role indicated by the `user` directive under `db`.
* The Redis process is started using `supervisorctl`. (Redis restores
  its database from `/var/lib/redis/dump.rdb` when it starts and
  saves the contents of the database to this file as well.)
* The `docassemble.webapp.create_tables` module is executed. The
  module performs the following actions.
    * If a file exists at `/configdata/initial_credentials`,
      the file is read using the `bash` command `source`. The purpose
      of this file is to provide definitions of the `DA_ADMIN_EMAIL`,
      `DA_ADMIN_PASSWORD`, and `DA_ADMIN_API_KEY` environment
      variables. After the file is read, it is deleted.
    * The module runs, which ensures that all of the necessary SQL
      database tables are created if they do not exist, and performs
      any necessary upgrades using [Alembic].
    * If the database was empty, the database is populated with
      default values. Most importantly, an administrative user is
      created. The credentials for this user are obtained from the
      `DA_ADMIN_EMAIL` and `DA_ADMIN_PASSWORD` environment variables,
      but if the environment variables are not defined,
      `admin@example.com` and `password` are used.
    * If the `DA_ADMIN_API_KEY` environment variable is defined, it is
      used to create an API key for the initial administrator user.
    * After the script is run, the `bash` script deletes the values of
      `DA_ADMIN_EMAIL`, `DA_ADMIN_PASSWORD`, and `DA_ADMIN_API_KEY`.
      Note that the values of `DA_ADMIN_EMAIL`, `DA_ADMIN_PASSWORD`,
      and `DA_ADMIN_API_KEY` are very sensitive. Although they can be
      defined through ordinary Docker environment variables, it is
      much safer to define them through the
      `/configdata/initial_credentials` file, which you can create
      with a Docker volume mount.
* The `docassemble.webapp.update` module is executed. When you install
  your own Python packages on a server, a list of the packages and
  their dependencies is kept in a SQL database table, so that if you
  perform a system upgrade, **docassemble** knows which packages need
  to be installed on the new server. This is accomplished through the
  `docassemble.webapp.update` module.
* The `rabbitmq` process is started using `supervisorctl`.
* The `celery` and `celerysingle` processes are started using
  `supervisorctl`.
* If Let's Encrypt is being used, then:
    * The `nascent` process is stopped so that Let's Encrypt can
      run. The `supervisord` daemon had already started the `nascent`
      process immediately when the container started.
    * `certbot` is run either to renew the certificate (if Let's
      Encrypt is already enabled for the given `DAHOSTNAME`) or create
      the certificate.
    * The Let's Encrypt configuration is copied to the data storage
      area.
* The `websockets` process is started using `supervisorctl`.
* The `uwsgi` process is started using `supervisorctl`.
* If the `nascent` process has not been stopped yet, it is stopped.
* The `nginx` process is started using `supervisorctl`.
* The root of the web application is accessed with `curl`. This is
  done because the first HTTP request made to the web application
  takes longer, so if that request is made immediately, hopefully no
  end user will encounter it.
* The `cron` process is started using `supervisorctl`.
* The `exim4` process is started using `supervisorctl`.

## <a name="hourly cron"></a>What happens during the hourly cron job

On an hourly basis, the `cron` process runs each of the scripts in
`/etc/cron.hourly/`, including the script
`/etc/cron.hourly/docassemble`.

The `/etc/cron.hourly/docassemble` script does the following:

* Hourly [scheduled tasks] are run.
* Temporary files in `/tmp` are deleted if they are more than a few
  hours old.
* The `docassemble.webapp.cleanup_sessions` module is run, which
  deletes stale Flask sessions.
* [NGINX] log files are copied to `/usr/share/docassemble/log`.
* If [S3] or [Azure Blob Storage] is not in use, files in
  `/usr/share/docassemble/files` are copied to data storage. This
  means that during the shutdown process, fewer files will need to be
  copied.

## <a name="daily cron"></a>What happens during the daily cron job

On a daily basis, the `cron` process runs each of the scripts in
`/etc/cron.daily/`, including the script
`/etc/cron.daily/docassemble`.

The `/etc/cron.daily/docassemble` script does the following:

* Daily [scheduled tasks] are run.
* If Let's Encrypt is in use, `certbot renew` is run for the
  `DAHOSTNAME`.
* The directory `/etc/letsencrypt` is copied to data storage as
  `letsencrypt.tar.gz`.
* The log files are copied to data storage.
* Every database that the PostgreSQL server hosts (except for ones with
  `template` in the name) are dumped to the `postgres` folder in data
  storage using `pg_dump -F c`.
* The `/var/lib/redis/dump.rdb` file is copied to data storage as the
  `redis.rdb` file.
* The `/usr/share/docassemble/files` directory containing uploaded and
  generated files, as well as the contents of users' Playgrounds, is
  copied to data storage. (This is not done if [S3] or [Azure Blob
  Storage] is used, because in that case the files live in the
  cloud and are copied to `/tmp` on an as-needed basis.)
* A rolling backup directory is created at, for example
  `/usr/share/docassemble/backup/07-01` (if today's date is July 1)
  and populated with:
    * `letsencrypt.tar.gz`, if Let's Encrypt is used.
    * A copy of the `postgres` directory containing each database that
      the SQL server hosts.
    * The `redis.rdb` file.
    * The log files.
    * The `files` directory, unless the [`backup file storage`]
      Configuration directive is false.
* If [S3] or [Azure Blob Storage] is used, the rolling backup is
  copied to the cloud.
* Rolling backup directories in `/usr/share/docassemble/backup` with
  modification times older than [`backup days`] days old are
  deleted. If [S3] or [Azure Blob Storage] is used, the same rolling
  backup directories are deleted from the cloud as well.

The `cron` process also calls `logrotate`, which rotates log
files.

The docassemble-specific `logrotate` files include
`/etc/logrotate.d/docassemble`, which contains the following.

{% highlight text %}
/usr/share/docassemble/log/docassemble.log
/usr/share/docassemble/log/apache_access.log
/usr/share/docassemble/log/apache_error.log
/usr/share/docassemble/log/nginx_access.log
/usr/share/docassemble/log/nginx_error.log
/usr/share/docassemble/log/uwsgi.log
/usr/share/docassemble/log/websockets.log
/usr/share/docassemble/log/worker.log
/usr/share/docassemble/log/single_worker.log
{
        su www-data www-data
        create 600 www-data www-data
        rotate 7
        maxsize 5M
        daily
        missingok
        notifempty
        postrotate
                /usr/share/docassemble/webapp/restart-post-logrotate.sh
        endscript
}
{% endhighlight %}

Another `logrotate` file that is relevant is `/etc/logrotate.d/nginx`,
which contains the following.

{% highlight text %}
/var/log/nginx/*.log {
        daily
        missingok
        rotate 7
        compress
        delaycompress
        notifempty
        create 0640 www-data adm
        sharedscripts
        prerotate
                if [ -d /etc/logrotate.d/httpd-prerotate ]; then \
                        run-parts /etc/logrotate.d/httpd-prerotate; \
                fi \
        endscript
        postrotate
                if /etc/init.d/nginx status > /dev/null ; then \
                        /usr/share/docassemble/webapp/restart-nginx.sh ; \
                fi
        endscript
}
{% endhighlight %}

## <a name="weekly cron"></a>What happens during the weekly cron job

On a weekly basis, the `cron` process runs each of the scripts in
`/etc/cron.weekly/`, including the script
`/etc/cron.weekly/docassemble`.

The `/etc/cron.weekly/docassemble` script does the following:

* Weekly [scheduled tasks] are run.

## <a name="monthly cron"></a>What happens during the monthly cron job

On a monthly basis, the `cron` process runs each of the scripts in
`/etc/cron.monthly/`, including the script
`/etc/cron.monthly/docassemble`.

The `/etc/cron.monthly/docassemble` script does the following:

* Monthly [scheduled tasks] are run.

## <a name="stop"></a>What happens during shut down

If the `supervisord` process receives the `SIGINT` or `SIGHUP` signal,
for example because a `docker stop` command was executed,
`supervisord` sends that signal to each of its running processes.

Upon receiving the signal, the `postgres` process does the following:

* Each database that the PostgreSQL server hosts (except for ones with
  `template` in the name) are dumped to the `postgres` folder in data
  storage using `pg_dump -F c`.
* The server is stopped with `pg_ctlcluster --force 14.9 main stop`.
* The process exits with exit code 0.

Upon receiving the signal to stop, the `redis` process does the
following:

* The server is stopped with `redis-cli shutdown`.
* The `/var/lib/redis/dump.rdb` file is copied to data storage as the
  `redis.drb` file.
* The process exits with exit code 0.

Upon receiving the signal to stop, the `initialize` process does the
following:

* The Configuration is copied to data storage. (This is not done if
  [S3] or [Azure Blob Storage] is used because the Configuration file
  is saved to the cloud immediately after being edited on the
  Configuration page.)
* Log files are copied to data storage.
* The `/usr/share/docassemble/files` directory containing uploaded and
  generated files, as well as the contents of users' Playgrounds, is
  copied to data storage. (This is not done if [S3] or [Azure Blob
  Storage] is used, because in that case the files live in the cloud
  and are copied to `/tmp` on an as-needed basis.)
* The script waits for the `postgres` shutdown process to complete
  successfully.
* The script waits for the `redis` shutdown process to complete
  successfully.
* Disk usage is tested, and if it is 100%, the process exits with exit
  code `1`.
* The process exits with exit code `0`.

The other processes stop without performing any additional tasks.

# <a name="nointernet"></a>Running without an internet connection

If you wish to run **docassemble** without a connection to the
internet, it should work. Some features will be unavailable, of
course, such as features that interact with [GitHub] and [Google
Cloud].

If the server will not have access to the internet, you may wish to
set `DAALLOWUPDATES` to `false` so that **docassemble** will not try
to run `apt -q -y update` during the initialization
process. However, even if you don't change `DAALLOWUPDATES`, the
**docassemble** container should still start properly, because if
`apt` cannot find a server it will fail and move on.

# <a name="troubleshooting"></a>Troubleshooting

If you are having trouble with your **docassemble** server, do not
assume that "turning it off and turning it on again" is a solution
that will fix whatever problems you are having. Maybe that is true
with some systems, but it is not true with Linux or **docassemble**.
In fact, if you are new to **docassemble**, "turning it off and
turning it on again" may make your problems much worse. Instead of
forcibly rebooting your system and hoping for the best, learn how to
access log files and uncover evidence about why your system is not
working as it should. (This section explains how.)  If you would like
to be able to "pull the plug" on your **docassemble** system without
negative repercussions, you can, if you first configure an external
SQL server, an external Redis server, and a cloud-based persistent
storage system. But until you have an external SQL server, an
external Redis server, and cloud-based persistent storage system, you
need to be extremely careful about how you shut down your Docker
container. (See the section on [shutting down](#shutdown) to learn
why.)

When something goes wrong, the first thing to check is the server's
log files. The error message that appears in the web browser often
does not contain a complete explanation of the error; the details may
be written to the log files and the user may only see a announcement
that there was an error. The server maintains several different log
files for different purposes. The most important log files are
available in the web browser on the [Logs] screen.

On the [Logs] screen, `docassemble.log` is the primary log file for
**docassemble** itself. `uwsgi.log` is the log file for [uWSGI], the
web server for Python applications. This file contains a log of HTTP
requests and the output of subprocesses called by
**docassemble**. `worker.log` is the log file for the [Celery] system,
which runs [background processes]. The Package Management screen uses
[background processes] to run package installation and upgrade
operations, so if it fails without giving you a log of its operations,
you can check `worker.log`.

Normally, you will not need to access the running container in order
to get **docassemble** to work, and all the log files you need will be
available from [Logs] in the web browser. However, you might want or
need to gain access to the running container in some circumstances,
such as when the [Logs] interface is not available, or when you need
to check a log file that isn't available at [Logs].

To access the Docker container, first connect to the host computer
using the command line (the same way you connected to the host
computer to run `docker run` initially). Then find out the ID of the
running container by doing [`docker ps`]. You will see output like
the following:

{% highlight text %}
CONTAINER ID  IMAGE  COMMAND  CREATED  STATUS  PORTS  NAMES
e4fa52ba540e  jhpyle/docassemble  "/usr/bin/supervisord" ...
{% endhighlight %}

The ID is in the first column. Then run:

{% highlight bash %}
docker exec -t -i e4fa52ba540e /bin/bash
{% endhighlight %}

using your own ID in place of `e4fa52ba540e`. This will give you a
[bash] command prompt within the running container.

The first thing to check when you connect to a container is:

{% highlight bash %}
supervisorctl status
{% endhighlight %}

The output should be something like:

{% highlight text %}
apache2                          STOPPED   Not started
celery                           RUNNING   pid 978, uptime 0:01:57
celerysingle                     RUNNING   pid 1045, uptime 0:01:52
cron                             RUNNING   pid 1291, uptime 0:01:34
exim4                            RUNNING   pid 1327, uptime 0:01:32
main:initialize                  RUNNING   pid 7, uptime 0:02:21
main:postgres                    RUNNING   pid 523, uptime 0:02:17
main:redis                       RUNNING   pid 572, uptime 0:02:09
nascent                          STOPPED   Aug 20 08:05 PM
nginx                            RUNNING   pid 1232, uptime 0:01:39
rabbitmq                         RUNNING   pid 793, uptime 0:02:02
reset                            STOPPED   Not started
sync                             STOPPED   Not started
syslogng                         STOPPED   Not started
unoconv                          RUNNING   pid 1275, uptime 0:01:37
update                           STOPPED   Not started
uwsgi                            RUNNING   pid 1148, uptime 0:01:44
watchdog                         RUNNING   pid 9, uptime 0:02:21
websockets                       RUNNING   pid 1107, uptime 0:01:46
{% endhighlight %}

If you are running **docassemble** in a single-server arrangement, the
processes that should be "RUNNING" include `celery`, `celerysingle`,
`cron`, `exim4`, `initialize`, `nginx`, `postgres`, `rabbitmq`,
`redis`, `unoconv`, `uwsgi`, `watchdog`, and `websockets`. (The
`initialize`, `postgres`, and `redis` processes are prefixed with
`main:` because they are combined into a group called `main` so that
they shut down simultaneously.)

[Supervisor] is the application that orchestrates the various services
that are necessary for the server to start up and operate. It creates
various log files in the `/var/log/supervisor` directory on the
server. For example, these files show the log for the `initialize`
process, which is responsible for starting the server:

* `/var/log/supervisor/initialize-stderr---supervisor-*.log`
* `/var/log/supervisor/initialize-stdout---supervisor-*.log`

Other log files on the container that you might wish to check, in
declining order of importance, are:

* `/usr/share/docassemble/log/docassemble.log` (log for the web application)
* `/usr/share/docassemble/log/worker.log` (log for [background processes])
* `/usr/share/docassemble/log/uwsgi.log` (log for the core of the web application)
* `/var/log/nginx/error.log` (log for the web server)
* `/var/log/supervisor/postgres-stderr---supervisor-*.log` (log for
  the SQL server)
* Other files in `/var/log/supervisor/` (logs for other services)
* `/usr/share/docassemble/log/websockets.log` (log for parts of the
  [live help] feature)
* `/var/spool/mail/mail` (log for [scheduled tasks], generated by `cron`)
* `/tmp/flask.log` (log used by [Flask] in rare situations)

To navigate through the directories on the system, use [`cd`] to
change your current directory and [`ls`] to list the files in a
directory. To view the contents of a file, type, e.g.,:

{% highlight bash %}
less /usr/share/docassemble/log/docassemble.log
{% endhighlight %}

Inside the [`less`] program, you can type spacebar to go to the next
page, `G` to go to the end of the file, `1G` to go to the start of the
file, and `q` to quit.

Enter `exit` to leave the container and get back to your standard
command prompt.

If `supervisorctl status` shows that the `initialize` service is in
`EXITED` or `FAILED` status, then there should be an error message in
the file `/var/log/supervisor/initialize-stderr---supervisor-*.log`
indicating what went wrong that prevented **docassemble** from
initializing. You will need to fix that problem, then type `exit` to
leave the container, and then restart your container by doing `docker
stop -t 600 <containerid>` followed by `docker start <containerid>`.

If `initialize` is `RUNNING` but `celery` is not `RUNNING`, and
`nascent` is still `RUNNING`, then your server is still in the process
of starting up. If it is taking a really long time to start up, check
the above log files to see where in the process it is getting stuck.

If you are get a "server error" in your web browser when trying to
access **docassemble**, there should be an error message in
`/usr/share/docassemble/log/uwsgi.log`. If you see a message about a
"blueprint's name collision," this is almost always not the real
error; you need to scroll up through several error messages to find
the actual error. When the web application crashes, the error that
initiated the crash causes other errors inside of the code of the
[Flask] framework, and a "blueprint's name collision" error is
typically the last error to be recorded in the error log.

If you encounter a problem with upgrading or installing packages,
check `/usr/share/docassemble/log/worker.log`. This is the error log
for the [Celery] background process system. A [Celery] background
task controls the upgrading and installation of packages, so if you
get an error during upgrading or installation of packages, make sure
to check here first.

If you need to change the [Configuration] but you cannot use the [web
interface] to do so because your container failed to start, or the web
application does not work, you can edit the [Configuration] manually.
The main configuration file is located at
`/usr/share/docassemble/config/config.yml`.

Because of the way that [data storage] works, however, you need to be
careful about editing the [Configuration] file directly. If you are
using [S3](#persistent S3) or [Azure Blob Storage](#persistent azure),
then during the container initialization process, the file will be
overwritten with the copy of `config.yml` that is stored in the cloud.
If you are not using cloud-based [data storage], then when a container
safely shuts down, `/usr/share/docassemble/config/config.yml` will be
copied to `/usr/share/docassemble/backup/config.yml`, and when a
container starts up, `/usr/share/docassemble/backup/config.yml` will
be copied to `/usr/share/docassemble/config/config.yml`, overwriting
the existing contents. This is part of the operation of the [data
storage] feature; it makes it possible for you to remove a container
and `docker run` a new one while retaining all of your data.

If you are using [S3](#persistent S3) or [Azure Blob
Storage](#persistent azure), then you should [`docker stop -t 600`] the
container, then edit the `config.yml` file through the cloud service
web interface (usually by downloading, editing, and uploading), and
then `docker start` the container again.

If you are not using [S3](#persistent S3) or [Azure Blob
Storage](#persistent azure), then you can edit the [Configuration]
file using an editor like [`nano`]. If the status of `initialize` is
`RUNNING`, edit `/usr/share/docassemble/config/config.yml` file, and
then do `supervisorctl start reset` to restart the **docassemble**
services so that they use the new [Configuration]. When the container
stops, it will safely shut down, and
`/usr/share/docassemble/config/config.yml` will be backed up to
`/usr/share/docassemble/backup/config.yml`. If you are using
[persistent volumes], the `backup` folder will be in the [Docker
volume] that will persist even if you `docker rm` the container. If
the status of `initialize` is `FAILED` or `EXITED`, then this backup
process will not take place; in that case, you should make your
changes to `/usr/share/docassemble/backup/config.yml`, and then
restart your container by doing [`docker stop -t 600`] followed by
`docker start`.

If you need to make manual changes to the installation of [Python]
packages, note that **docassemble**'s [Python] code is installed in a
[Python virtual environment] in which all of the files are readable
and writable by the `www-data` user. The virtual environment is
located at `/usr/share/docassemble/local3.12/`. Thus, installing
[Python] packages through Ubuntu's `apt` utility will not actually
make that [Python] code available to **docassemble**. Before using
[pip], you need to first change the user to `www-data`, and then
switch into the appropriate [Python virtual environment].

{% highlight bash %}
su www-data
source /usr/share/docassemble/local3.12/bin/activate
{% endhighlight %}

Note that if you want to install a new version of a [Python] package
that may already be installed, you will want to use the `--upgrade`
and `--force-reinstall` parameters.

{% highlight bash %}
pip install --upgrade --force-reinstall azure-storage
{% endhighlight %}

To stop using the [Python virtual environment], type the command
`deactivate`. To stop being the `www-data` user, type the command
`exit`.

Services other than [NGINX] and [uWSGI] are an important part of
**docassemble**'s operations. For example, the upgrading and
installation of [Python] packages takes place in a background process
operated by the `celery` service. In addition, the [live help]
feature uses a service called `websockets`. The `nginx`, `uwsgi`,
`celery`, and `websockets` services all need to be restarted every
time there is a change to the [Configuration] or a change to [Python]
code. To restart all of the services at once, you can do:

{% highlight bash %}
supervisorctl start reset
{% endhighlight %}

However, if the `uwsgi` process has crashed, then you need to do:

{% highlight bash %}
supervisorctl restart uwsgi
supervisorctl start reset
{% endhighlight %}

You need to manually restart the `uwsgi` process here because the
`reset` process uses an optimized method of refreshing the application
server. This usually works well when you make [Configuration] and
[Python] code changes, but if [uWSGI] has crashed, `supervisorctl
start reset` will not bring it back to life.

If you want to access the [Redis] data, do [`docker exec`] to get
inside the container and then run `redis-cli` (assuming that your
[Redis] server is the default local [Redis] server). Note that
**docassemble** uses several of the [Redis] databases. If you do
`redis-cli -n 1` (the default), you will access the database used on a
system level. If you do `redis-cli -n 2`, you will access the
database used by [`DARedis`].

Unless you specify a different SQL server, the [PostgreSQL] data for
your **docassemble** server is inside the `docassemble` database
running on the Docker container. The default username is
`docassemble` and the default password is `abc123`. After doing
[`docker exec`] to get inside the container, run:

{% highlight bash %}
psql -U docassemble -d docassemble -h localhost -W
{% endhighlight %}

When prompted, enter password `abc123`.

For more information about troubleshooting **docassemble**, see
the [debugging subsection] of the [installation] section.

# <a name="configuration options"></a>Configuration options

In the example [above](#single server arrangement), we started
**docassemble** with `docker run -d -p 80:80 jhpyle/docassemble`.
This command will cause **docassemble** to use default values for all
configuration options. You can also communicate specific
configuration options to the container.

The recommended way to do this is to create a text file called
`env.list` in the current working directory containing environment
variable definitions in standard shell script format. For example:

{% highlight text %}
DAHOSTNAME=docassemble.example.com
USEHTTPS=true
USELETSENCRYPT=true
LETSENCRYPTEMAIL=admin@example.com
{% endhighlight %}

Then, you can pass these environment variables to the container using
the [`docker run`] command:

{% highlight bash %}
docker run --env-file=env.list -d -p 80:80 -p 443:443 --restart always --stop-timeout 600 jhpyle/docassemble
{% endhighlight %}

These configuration options will cause [NGINX] to use
docassemble.example.com as the server name and use [HTTPS] with
certificates hosted on [Let's Encrypt]. (The flag `-p 443:443` is
included so that the [HTTPS] port is exposed.)

If you want your server to be able to accept incoming [e-mails], you
will need to add `-p 25:25 -p 465:465` in order to open ports 25
and 465. See the [e-mailing the interview] section for information
about configuring your server to receive e-mails.

A [template for the `env.list` file] is included in distribution.

When running **docassemble** in [ECS], environment variables like
these are specified in [JSON] text that is entered into the web
interface. (See the [scalability] section for more information about
using [ECS].)

In your `env.list` file, you can set a variety of options. These
options are case specific, so you need to literally specify `true` or
`false`, because `True` and `False` will not work.

The following two options are specific to the particular server being
started (which, in a [multi-server arrangement], will vary from server
to server).

* <a name="CONTAINERROLE"></a>`CONTAINERROLE`: either `all` or a
  colon-separated list of services (e.g. `web:celery`,
  `sql:log:redis`, etc.) that should be started by the server. Only
  set the `CONTAINERROLE` if you are using a [multi-server
  arrangement]; the default is `all`. The available options
  are:
  * `all`: the [Docker] container will run all of the services of
    **docassemble** on a single container.
  * `web`: The [Docker] container will serve as a web server.
  * `celery`: The [Docker] container will serve as a [Celery] node.
  * `sql`: The [Docker] container will run the central [PostgreSQL] service.
  * `cron`: The [Docker] container will run [scheduled tasks] and
    other necessary tasks, such as updating SQL tables.
  * `redis`: The [Docker] container will run the central [Redis] service.
  * `rabbitmq`: The [Docker] container will run the central [RabbitMQ] service.
  * `log`: The [Docker] container will run the central log aggregation service.
  * `mail`: The [Docker] container will run [Exim] in order to accept [e-mails].
* <a name="SERVERHOSTNAME"></a>`SERVERHOSTNAME`: In a
  [multi-server arrangement], all **docassemble** application servers
  need to be able to communicate with each other using port 9001 (the
  [supervisor] port). All application servers "register" with the
  central SQL server. When they register, they each provide their
  hostname; that is, the hostname at which the specific individual
  application server can be found. Then, when an application server
  wants to send a message to the other application servers, the
  application server can query the central SQL server to get a list of
  hostnames of other application servers. This is necessary so that
  any one application server can send a signal to the other
  application servers to install a new package or a new version of a
  package, so that all servers are running the same software. If you
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

The following options, if you choose to set them, need to be set using
Docker environment variables at the time of the initial `docker
run`. The values are needed immediately when the container first
starts, so they cannot be set through a `config.yml` file. Setting
these options is not required; these options are used to provide
increased security within a [multi-server arrangement], in which
servers send each other commands over port 9001.

* `DASUPERVISORUSERNAME`: the username that should be used when
  communicating with [supervisor] over port 9001.
* `DASUPERVISORPASSWORD`: the password that should be used when
  communicating with [supervisor] over port 9001.

These variables will be populated in the [Configuration] under the
[`supervisor`] directive.

The following eight options indicate where an existing configuration
file can be found on [S3](#persistent s3) or
[Azure blob storage](#persistent azure). If a [configuration] file
exists in the cloud at the indicated location, that [configuration]
file will be used to set the [configuration] of your **docassemble**
installation. If no [configuration] file yet exists in the cloud at the
indicated location, **docassemble** will create an initial
[configuration] file and store it in the indicated location.

* <a name="S3ENABLE"></a>`S3ENABLE`: Set this to `true` if you are
  using [S3] (or [S3]-compatible object storage service) as a
  repository for uploaded files, [Playground] files, the
  [configuration] file, and other information. This environment
  variable, along with others that begin with `S3`, populates values
  in [`s3` section] of the initial [configuration] file. If this is
  unset, but [`S3BUCKET`] is set, it will be assumed to be `true`.
* <a name="S3BUCKET"></a>`S3BUCKET`: If you are using [S3], set this
  to the bucket name. Note that **docassemble** will not create the
  bucket for you. You will need to create it for yourself
  beforehand. The bucket should be empty.
* <a name="S3ACCESSKEY"></a>`S3ACCESSKEY`: If you are using [S3], set
  this to the [S3] access key. You can ignore this environment
  variable if you are using [EC2] with an [IAM] role that allows
  access to your [S3] bucket.
* <a name="S3SECRETACCESSKEY"></a>`S3SECRETACCESSKEY`: If you are
  using [S3], set this to the [S3] access secret. You can ignore this
  environment variable if you are using [EC2] with an [IAM] role that
  allows access to your [S3] bucket.
* <a name="S3REGION"></a>`S3REGION`: If you are using [S3], set this
  to the [region] you are using (e.g., `us-west-1`, `us-west-2`,
  `ca-central-1`).
* <a name="S3ENDPOINTURL"></a>`S3ENDPOINTURL`: If you are using a
  non-[AWS]<span></span> [S3]-compatible object storage service, set
  `S3ENDPOINTURL` to the URL of the service, (e.g.,
  `https://region.mys3service.com`. Usually this URL does not contain
  the bucket name (e.g., not
  `https://bucket.region.mys3service.com`). If you have trouble
  connecting to a third-party S3 endpoint, you might want to try
  setting `AWS_REQUEST_CHECKSUM_CALCULATION=WHEN_REQUIRED` in the
  environment variables.
* <a name="S3_SSE_ALGORITHM"></a>`S3_SSE_ALGORITHM`: the server-side
  encryption algorithm used (e.g., `AES256`, `aws:kms`). This should
  only be specified if the S3 bucket uses server-side encryption.
* <a name="S3_SSE_CUSTOMER_ALGORITHM"></a>`S3_SSE_CUSTOMER_ALGORITHM`: the
  server-side encryption algorithm used (e.g., `AES256`,
  `aws:kms`). This should only be specified if the S3 bucket uses
  server-side encryption and you are passing an `S3_SSE_CUSTOMER_KEY`.
* <a name="S3_SSE_CUSTOMER_KEY"></a>`S3_SSE_CUSTOMER_KEY`: the
  encryption key used when encrypting data. This should only be
  specified if the S3 bucket uses server-side encryption and you have
  specified an `S3_SSE_CUSTOMER_ALGORITHM`.
* <a name="S3_SSE_KMS_KEY_ID"></a>`S3_SSE_KMS_KEY_ID`: the AWS KMS key
  ID to use for object encryption. This should only be specified if
  the S3 bucket uses server-side encryption.
* <a name="AZUREENABLE"></a>`AZUREENABLE`: Set this to `true` if you
  are using [Azure blob storage](#persistent azure) as a repository
  for uploaded files, [Playground] files, the [configuration] file,
  and other information. This environment variable, along with others
  that begin with `AZURE`, populates values in [`azure` section] of
  the [configuration] file. If this is unset, but
  [`AZUREACCOUNTNAME`], [`AZUREACCOUNTKEY`], and [`AZURECONTAINER`]
  are set, it will be assumed to be `true`.
* <a name="AZURECONTAINER"></a>`AZURECONTAINER`: If you are using
  [Azure blob storage](#persistent azure), set this to the container
  name. Note that **docassemble** will not create the container for you.
  You will need to create it for yourself beforehand.
* <a name="AZUREACCOUNTNAME"></a>`AZUREACCOUNTNAME`: If you are using
  [Azure blob storage](#persistent azure), set this to the account
  name.
* <a name="AZUREACCOUNTKEY"></a>`AZUREACCOUNTKEY`: If you are
  using [Azure blob storage], set this to the account key.

The options listed below are "setup" parameters that are useful for
pre-populating a fresh [configuration] with particular values. These
environment variables are effective only during an initial `run` of
the [Docker] container, when a [configuration] file does not already
exist.

If you are using [persistent volumes], or you have set the options
above for [S3](#persistent s3)/[Azure blob storage](#persistent azure)
and a [configuration] file exists in your cloud storage, the values in
that stored [configuration] file will, by default, take precedence
over any values you specify in `env.list`. If you are using
[S3](#persistent s3)/[Azure blob storage](#persistent azure), you can
edit these configuration files in the cloud and then stop and start
your container for the new configuration to take effect.

* <a name="DAWEBSERVER"></a>`DAWEBSERVER`: This can be set either to
  `nginx` (the default) or `apache`. See the [`web server`]
  configuration directive.
* <a name="DBHOST"></a>`DBHOST`: The hostname of the [PostgreSQL]
  server. Keep undefined or set to `null` in order to use the
  [PostgreSQL] server on the same host. This environment variable,
  along with others that begin with `DB`, populates values in [`db`
  section] of the [configuration] file. If you are using a managed
  SQL database service, set `DBHOST` to the hostname of the database
  service. If you are using [PostgreSQL] and the database referenced
  by `DBNAME` does not exist on the SQL server, the [Docker] startup
  process will attempt to use the `DBUSER` and `DBPASSWORD`
  credentials to create the database. Otherwise, you need to make
  sure the database by the name of `DBNAME` exists before
  **docassemble** starts.
* <a name="DBNAME"></a>`DBNAME`: The name of the database. The
  default is `docassemble`.
* <a name="DBUSER"></a>`DBUSER`: The username for connecting to the
  [PostgreSQL] server. The default is `docassemble`.
* <a name="DBPASSWORD"></a>`DBPASSWORD`: The password for connecting
  to the SQL server. The default is `abc123`. Valid characters include
  alphanumeric characters, `_`, `~`, `/`, `-`, `^`, `*`, `?`, and `!`.
* <a name="DBPREFIX"></a>`DBPREFIX`: This sets the prefix for the
  database specifier. The default is `postgresql+psycopg2://`. This
  corresponds with the `prefix` of the [`db`] configuration directive.
* <a name="DBPORT"></a>`DBPORT`: This sets the port that
  **docassemble** will use to access the SQL server. If you are using
  the default port for your database backend, you do not need to set
  this.
* <a name="DBTABLEPREFIX"></a>`DBTABLEPREFIX`: This allows multiple
  separate **docassemble** implementations to share the same SQL
  database. The value is a prefix to be added to each table in the
  database.
* <a name="DBBACKUP"></a>`DBBACKUP`: Set this to `false` if you are
  using an off-site [PostgreSQL] `DBHOST` and you do not want the
  database to be backed up by the daily cron job. This is important
  if the off-site SQL database is large compared to the available disk
  space on the server. The default value is `true`.
* <a name="DBSSLMODE"></a>`DBSSLMODE`: This is relevant if you have a
  [PostgreSQL] database and you have an SSL certificate for it. This
  sets the `sslmode` parameter. For more information, see the
  documentation for the [`db` section] of the [Configuration].
* <a name="DBSSLCERT"></a>`DBSSLCERT`: This is relevant if you have a
  [PostgreSQL] database and you have an SSL certificate for it. This
  is the name of a certificate file. For more information, see the
  documentation for the [`db` section] of the [Configuration].
* <a name="DBSSLKEY"></a>`DBSSLKEY`: This is relevant if you have a
  [PostgreSQL] database and you have an SSL certificate for it. This
  is the name of a certificate key file. For more information, see the
  documentation for the [`db` section] of the [Configuration].
* <a name="DBSSLROOTCERT"></a>`DBSSLROOTCERT`: This is relevant if you
  have a [PostgreSQL] database and you have an SSL certificate for
  it. This is the name of a root certificate file. For more
  information, see the documentation for the [`db` section] of the
  [Configuration].
* <a name="DASQLPING"></a>`DASQLPING`: If your docassemble server runs
  in an environment in which persistent SQL connections will
  periodically be severed, you can set `DASQLPING: true` in order to
  avoid errors. There is an overhead cost to using this, so only
  enable this if you get SQL errors when trying to connect after a
  period of inactivity. The default is `false`. See the [`sql ping`]
  configuration directive.
* <a name="EC2"></a>`EC2`: Set this to `true` if you are running
  [Docker] on [EC2]. This tells **docassemble** that it can use an
  [EC2]-specific method of determining the hostname of the server on
  which it is running. See the [`ec2`] configuration directive.
* <a name="COLLECTSTATISTICS"></a>`COLLECTSTATISTICS`: Set this to
  `true` if you want the server to use [Redis] to track the number of
  interview sessions initiated. See the [`collect statistics`]
  configuration directive.
* <a name="KUBERNETES"></a>`KUBERNETES`: Set this to `true` if you are
  running inside [Kubernetes]. This tells **docassemble** that it can
  use the IP address of the Pod in place of the hostname. See the
  [`kubernetes`] configuration directive.
* <a name="USEHTTPS"></a>`USEHTTPS`: Set this to `true` if you would
  like **docassemble** to communicate with the browser using
  encryption. Read the [HTTPS] section for more information.
  Defaults to `false`. See the [`use https`] configuration directive.
  Do not set this to `true` if you are using a proxy server that
  forwards non-encrypted [HTTP] to your server; in that case, see the
  [`BEHINDHTTPSLOADBALANCER`] variable below.
* <a name="DAHOSTNAME"></a>`DAHOSTNAME`: Set this to the hostname by
  which web browsers can find **docassemble**. This is necessary for
  [HTTPS] to function. See the [`external hostname`] configuration
  directive.
* <a name="USELETSENCRYPT"></a>`USELETSENCRYPT`: Set this to `true` if
  you are [using Let's Encrypt]. The default is `false`. See the
  [`use lets encrypt`] configuration directive.
* <a name="LETSENCRYPTEMAIL"></a>`LETSENCRYPTEMAIL`: Set this to the
  e-mail address you use with [Let's Encrypt]. See the
  [`lets encrypt email`] configuration directive.
* <a name="LOGSERVER"></a>`LOGSERVER`: This is used in the
  [multi-server arrangement] where there is a separate server for
  collecting log messages. The default is `none`, which causes the
  server to run [Syslog-ng]. See the [`log server`] configuration
  directive.
* <a name="REDIS"></a>`REDIS`: If you are running **docassemble** in a
  [multi-server arrangement], set this to `redis://thehostname` where
  `thehostname` is the host name at which the [Redis] server can be
  accessed. See the [`redis`] configuration directive.
* <a name="RABBITMQ"></a>`RABBITMQ`: If you are running
  **docassemble** in a [multi-server arrangement], set this to the URL
  at which the [RabbitMQ] server can be accessed, in the form
  `pyamqp://guest@rabbitmqserver.local//` or
  `pyamqp://user:xxsecretpasswdxx@rabbitmqserver.local//`. Note that
  [RabbitMQ] is very particular about hostnames. If the [RabbitMQ]
  server is running on a machine on which the command `hostname -s`
  evaluates to `rabbitmqserver.local`, then your application servers
  will need to use `rabbitmqserver.local` as the hostname in the
  `RABBITMQ` URL, even if other names resolve to the same IP address.
  Note that if you run **docassemble** using the instructions in the
  [scalability] section, you may not need to worry about setting
  `RABBITMQ`. See the [`rabbitmq`] configuration directive.
* <a name="DACELERYWORKERS"></a>`DACELERYWORKERS`: By default, the
  number of Celery workers is based on the number of CPUs on the
  machine and its total memory. If you want to set a different value,
  set `DACELERYWORKERS` to integer greater than or equal to 1. See the
  [`celery processes`] configuration directive.
* <a name="DAMAXCELERYWORKERS"></a>`DACELERYWORKERS`: By default, the
  number of Celery workers scales with the number of CPUs on the
  machine (one process per CPU reported by `nproc`) and is limited by
  the total memory (one process for every 2GB). If you want the number
  of Celery workers to scale based on the number of CPUs but the
  memory-based limit is to restrictive, you can set
  `DAMAXCELERYWORKERS` to integer greater than or equal to 1. See the
  [`max celery processes`] configuration directive.
* <a name="SERVERADMIN"></a>`SERVERADMIN`: If your **docassemble** web
  server generates an error, the error message will contain an e-mail
  address that the user can contact for help. This e-mail address
  defaults to `webmaster@localhost`. You can set this e-mail address
  by setting the `SERVERADMIN` environment variable to the e-mail
  address you want to use. See the [`server administrator email`]
  configuration directive.
* <a name="POSTURLROOT"></a>`POSTURLROOT`: If users access
  **docassemble** at https://docassemble.example.com/da, set `POSTURLROOT`
  to `/da/`. The trailing slash is important. If users access
  **docassemble** at https://docassemble.example.com, you can ignore
  this. The default value is `/`. See the [`root`] configuration
  directive.
* <a name="BEHINDHTTPSLOADBALANCER"></a>`BEHINDHTTPSLOADBALANCER`: Set
  this to `true` if you are using a load balancer or proxy server that
  accepts connections in HTTPS and forwards them to your server or
  servers as HTTP. This lets **docassemble** know that when it forms
  URLs, it should use the `https` scheme even though requests appear
  to be coming in as HTTP requests, and when it sends cookies, it
  should set the `secure` flag on the cookies. You also need to make
  sure that your proxy server is setting the `X-Forwarded-*` HTTP
  headers when it passes HTTP requests to your server or servers. See
  the [`behind https load balancer`] configuration directive for more
  information.
* <a name="XSENDFILE"></a>`XSENDFILE`: Set this to `false` if the
  X-Sendfile header is not functional in your configuration for
  whatever reason. See the [`xsendfile`] configuration directive.
* <a name="DAALLOWUPDATES"></a>`DAALLOWUPDATES`: Set this to `false`
  if you want to disable the updating of software through the user
  interface. See the [`allow updates`] configuration directive.
* <a name="DAUPDATEONSTART"></a>`DAUPDATEONSTART`: Set this to `false`
  if you do not want the container to update its software using `pip`
  when it starts up. Set `DAUPDATEONSTART` to `initial` if you want
  the container to update its software during the first `docker run`,
  but not on every `docker start`. See the [`update on start`]
  configuration directive.
* <a name="DAROOTOWNED"></a>`DAROOTOWNED`: Set this
  to `true` if you are setting `DAALLOWUPDATES=false` and
  `DAENABLEPLAYGROUND=false` you also want to take the extra step of
  making the directories containing code owned by `root` so that the
  web browser user cannot access them.
* <a
  name="DAALLOWCONFIGURATIONEDITING"></a>`DAALLOWCONFIGURATIONEDITING`:
  Set this to `false` to prevent the editing of the Configuration.
  See the [`allow configuration editing`] configuration directive.
* <a name="DAENABLEPLAYGROUND"></a>`DAENABLEPLAYGROUND`: Set this to
  `false` to disable the Playground on the server. See the
  [`enable playground`] directive.
* <a name="DAALLOWLOGVIEWING"></a>`DAALLOWLOGVIEWING`: Set this to
  `false` to prevent administrators and developers from viewing the
  system logs by going to Logs on the menu. By default, administrators
  and developers can access Logs.
* <a name="DADEBUG"></a>`DADEBUG`: Set this to `false` if you want the
  server to be in production mode rather than developer mode. This
  will also disable access to example and demonstration interviews in
  the `docassemble.base` and `docassemble.demo` packages. See the
  [`debug`] and [`allow demo`] configuration directives.
* <a name="TIMEZONE"></a>`TIMEZONE`: You can use this to set the time
  zone of the server. The value of the variable is stored in
  `/etc/timezone` and `dpkg-reconfigure -f noninteractive tzdata` is
  run in order to set the system time zone. The default is
  `America/New_York`. The time zone must exactly match the name of a
  time zone in the [tz database]. See the [`timezone`] configuration
  directive.
* <a name="LOCALE"></a>`LOCALE`: You can use this to enable a locale
  on the server. The value needs to exactly match one of the valid
  [locale values] that [Ubuntu]/[Debian] recognizes (listed in the
  `/etc/locale.gen` file on an [Ubuntu]/[Debian] system). When the
  server starts, the value of `LOCALE` is appended to
  `/etc/locale.gen` and `locale-gen` and `update-locale` are run. The
  default is `en_US.UTF-8 UTF-8`. See the [`os locale`] configuration
  directive.
* <a name="OTHERLOCALES"></a>`OTHERLOCALES`: You can use this to set
  up other locales on the system besides the default locale. Set this
  to a comma separated list of locales. The values need to match
  entries in `/etc/locale.gen` on [Ubuntu]. See the
  [`other os locales`] configuration directive.
* <a name="PACKAGES"></a>`PACKAGES`: If your interviews use code that
  depends on certain [Ubuntu] packages being installed, you can
  provide a comma-separated list of [Ubuntu] packages in the
  `PACKAGES` environment variable. The packages will be installed
  when the container is started. See the [`ubuntu packages`]
  configuration directive.
* <a name="PYTHONPACKAGES"></a>`PYTHONPACKAGES`: If you want to
  install certain [Python] packages during the container start process,
  you can provide a comma-separated list of packages in the
  `PYTHONPACKAGES` environment variable. See the [`python packages`]
  configuration directive.
* <a name="DASECRETKEY"></a>`DASECRETKEY`: The secret key for protecting
  against cross-site forgery. See the [`secretkey`] configuration
  directive. If `DASECRETKEY` is not set, a random secret key will be
  generated.
* <a name="DABACKUPDAYS"></a>`DABACKUPDAYS`: The number of days
  backups should be kept. The default is 14. See the [`backup days`]
  configuration directive.
* <a name="DAEXPOSEWEBSOCKETS"></a>`DAEXPOSEWEBSOCKETS`: You may need
  to set this to `true` if you are operating a [Docker] container
  [behind a reverse proxy] and you want to use the [WebSocket]-based
  [live help] features. See the [`expose websockets`] configuration
  directive.
* <a name="DAWEBSOCKETSIP"></a>`DAWEBSOCKETSIP`: You can set this if
  you need to manually specify the address on which the `websockets`
  service runs. See the [`websockets ip`] configuration directive.
* <a name="DAWEBSOCKETSPORT"></a>`DAWEBSOCKETSPORT`: You can set this
  if you need to manually specify the port on which the `websockets`
  service runs. See the [`websockets port`] configuration directive.
* <a name="PORT"></a>`PORT`: By default, if you are not using [HTTPS],
  the **docassemble** web application runs on port 80. When running
  Docker, you can map any port on the host to port 80 in the
  container. However, if you are using a system like Heroku which
  expects the Docker container to use the `PORT` environment variable,
  you can set `PORT` in your `env.list` file. See the [`http port`]
  configuration directive.
* <a name="USEMINIO"></a>`USEMINIO`: Set this to `true` if you are
  setting [`S3ENDPOINTURL`] to point to [MinIO] and you would like the
  bucket to be created when the container starts. See the [`use
  minio`] configuration directive.
* <a name="USECLOUDURLS"></a>`USECLOUDURLS`: Set this to `false` if
  you are using cloud storage but you do not want URLs for files to
  point directly to the cloud storage provider. See the [`use cloud
  urls`] configuration directive.
* <a name="DASTABLEVERSION"></a>`DASTABLEVERSION`: Set this to `true`
  if you want **docassemble** to stay on version 1.0.x. This is the
  `stable` branch of the [GitHub] repository, which only receives bug
  fixes and security updates. See the [`stable version`]
  configuration directive.
* <a name="DASSLPROTOCOLS"></a>`DASSLPROTOCOLS`: This indicates the
  SSL protocols that [NGINX] should accept. The default is `TLSv1.2
  TLSv1.3`.  You might want to set it to `TLSv1 TLSv1.1 TLSv1.2
  TLSv1.3` if you need to support older browsers. The value is passed
  directly to the [NGINX] directive [`ssl_protocols`]. See the [`nginx
  ssl protocols`] configuration directive.
* <a name="DASSLCIPHERS"></a>`DASSLCIPHERS`: This indicates the SSL
  ciphers that [NGINX] should accept. The default is
  `HIGH:!aNULL:!MD5`.  You might want to change it if you need to
  support older browsers or remove support for ciphers that are
  considered weak. The value is passed directly to the [NGINX]
  directive [`ssl_ciphers`]. See the [`nginx ssl ciphers`]
  configuration directive.
* <a name="PIPINDEXURL"></a>`PIPINDEXURL`: This controls the package
  index that `pip` uses. See the [`pip index url`] configuration
  directive.
* <a name="PIPEXTRAINDEXURLS"></a>`PIPEXTRAINDEXURLS`: This controls
  the extra package index sites that `pip` uses. See the [`pip extra
  index urls`] configuration directive.
* <a name="ENABLEUNOCONV"></a>`ENABLEUNOCONV`: This controls whether
  [unoconv] is used for DOCX to PDF conversion. It can be set to
  `true` or `false`. See the [`enable unoconv`] configuration
  directive.
* <a name="GOTENBERGURL"></a>`GOTENBERGURL`: This can be set to the
  URL of your [Gotenberg] server, if you have one. See the [`gotenberg
  url`] configuration directive.
* <a name="USENGINXTOSERVEFILES"></a>`USENGINXTOSERVEFILES`: If
  NGINX is not being used in the container (i.e. traffic is
  connected directly to `uwsgi`) then this should be
  `false`. Otherwise it should be `true`. The default is `true`. See
  the [`use nginx to serve files`] configuration directive.
* <a name="SUPERVISORLOGLEVEL"></a>`SUPERVISORLOGLEVEL`: This can be
  set to `debug` if you would like log messages to print to the output
  of `supervisord`, which is the output of the container itself. This
  allows you to view log messages using `docker logs`. The default
  value is `info`, which means that the output of `supervisord` is
  limited to messages about the starting and stopping of services and
  processes.
* <a
  name="ENVIRONMENT_TAKES_PRECEDENCE"></a>`ENVIRONMENT_TAKES_PRECEDENCE`:
  It was noted above that once the [configuration] file is located in
  the [persistent volume], [S3](#persistent s3), or [Azure blob
  storage](#persistent azure), the values in that [configuration] file
  will take precedence over any values specified in [Docker]
  environment variables. This is the default behavior; the [Docker]
  environment variables are useful for 1) telling the server where to
  find an existing [configuration] file; and 2) if no [configuration]
  file exists already, pre-populating the initial [configuration]
  file. However, if you set `ENVIRONMENT_TAKES_PRECEDENCE` to `true`,
  then **docassemble** will override values in the [configuration]
  file with the values of [Docker] environment variables if they
  conflict. Note that the [YAML] of the [configuration] file will not
  be altered; you will still see the same [YAML] when you go to edit
  the [Configuration]. However, internally, **docassemble** will
  override those values with the values of the [Docker] environment
  variables. Since it can be confusing to have dueling sources of
  configuration values, it is encouraged that you update the [YAML] of
  your [Configuration] to align with the values in your [Docker]
  environment. The `ENVIRONMENT_TAKES_PRECEDENCE` option is primarily
  used in the [Kubernetes]/[Helm] environment, where there are some
  [Docker] environment variables that cannot be known in advance.

## <a name="configuration"></a>Changing the configuration

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
persistent volume.

When **docassemble** starts up on a [Docker] container, it:

* Creates a [configuration] file from a template, using environment
  variables for initial values, if a [configuration] file does not
  already exist.
* Initializes a [PostgreSQL] database, if one is not already initialized.
* Configures the [NGINX] configuration, if one is not already
  configured.
* Runs [Let's Encrypt] if the configuration indicates that
  [Let's Encrypt] should be used, and [Let's Encrypt] has not yet been
  configured.

When **docassemble** stops, it saves the [configuration] file, a
backup of the [PostgreSQL] database, and backups of the [Let's Encrypt]
configuration. If you are using [persistent volumes], the information
will be stored there. If you are using [S3](#persistent s3) or [Azure
blob storage](#persistent azure), the information will be stored in
the cloud.

When **docassemble** starts again, it will retrieve the
[configuration] file, the backup of the [PostgreSQL] database, and
backups of the [Let's Encrypt] configuration from storage and use them
for the container.

Suppose you have an existing installation that uses HTTPS and [Let's
Encrypt], but you want to change the [`DAHOSTNAME`]. You will need to
delete the saved configuration before running a new container. First,
shut down the machine with [`docker stop -t 600`]. Then, if you are using
[S3](#persistent s3), you can go to the [S3 Console] and delete the
"letsencrypt.tar.gz" file. If you are using [Azure blob
storage](#persistent azure), you can go to the [Azure Portal] and
delete the "letsencrypt.tar.gz" file.

Also, if a configuration file exists on [S3](#persistent
s3)/[Azure blob storage](#persistent azure) (`config.yml`) or in a
[persistent volume], then the values in that configuration will take
precedence over the corresponding environment variables that are
passed to [Docker]. Once a configuration file exists, you should make
changes to the configuration file rather than passing environment
variables to [Docker]. However, if your configuration is on
[S3](#persistent s3)/[Azure blob storage](#persistent azure), you will
at least need to pass sufficient access keys (e.g., [`S3BUCKET`],
[`AZURECONTAINER`], etc.) to access that storage; otherwise your
container will not know where to find the configuration.

Also, there are some environment variables that do not exist in the
configuration file because they are specific to the individual server
being started. These include the [`CONTAINERROLE`] and
[`SERVERHOSTNAME`] environment variables.

# <a name="data storage"></a>Data storage

[Docker] containers are volatile. They are designed to be run, turned
off, and destroyed. When using [Docker], the best way to upgrade
**docassemble** to a new version is to destroy and rebuild your
containers.

But what about your data?  If you run **docassemble**, you are
accumulating valuable data in SQL, in files, and in [Redis]. If your
data are stored on the [Docker] container, they will be destroyed by
[`docker rm`].

There are two ways around this problem. The first, and most
preferable solution, is to use an object storage service. The
standard-setting object storage service is [Amazon Web Services]'s
[S3]. If you use [AWS], you can create an [S3 bucket] for your data,
and then when you launch your **docassemble** container, set the
[`S3BUCKET`], [`S3ACCESSKEY`], [`S3SECRETACCESSKEY`], and [`S3REGION`]
environment variables.

If you don't want to use [Amazon Web Services], you can use an
[S3]-compatible object storage service by setting [`S3ENDPOINTURL`] to
the URL of the service, along with the [`S3BUCKET`], [`S3ACCESSKEY`],
and [`S3SECRETACCESSKEY`]<span></span> [environment variables]. There
are [S3]-compatible object storage services available for [Google
Cloud], [Wasabi], [Linode], [Vultr], [Digital Ocean], [IBM Cloud],
[Oracle Cloud], [Scaleway], [Exoscale], and others. If you are
operating an on-premises server, you can deploy [MinIO] ([MinIO] is
configured by default if you deploy **docassemble** [with Kubernetes])
or [Rook].

In addition to [S3] and [S3]-compatible object storage,
**docassemble** supports [Azure blob storage]. You can create a [blob
storage container] inside [Microsoft Azure] and then when you launch
your container, you set the [`AZUREACCOUNTNAME`], [`AZUREACCOUNTKEY`],
and [`AZURECONTAINER`]<span></span> [environment variables].

When [`docker stop -t 600`] is run, **docassemble** will backup the SQL
database, the [Redis] database, the [configuration], and your uploaded
files to the [S3 bucket] or [blob storage container]. Then, when you
issue a [`docker run`] command with [environment variables] pointing
**docassemble** to your [S3 bucket]/[Azure blob storage] resource,
**docassemble** will make restore from the backup. You can [`docker
rm`] your container and your data will persist in the cloud.

The second method of persistent storage is to use [persistent
volumes], which is a feature of [Docker]. This will store the data in
directories on the [Docker] host, so that when you destroy the
container, these directories will be untouched, and when you start up
a new container, it will use the saved directories. This feature is
only available if you are running **docassemble** in a single-server
configuration.

These two options are explained in the following subsections.

If you are operating a development server in a single-server
configuration, and you will be using the [Playground], using
[persistent volumes] is recommended. When a development server uses
[S3], every time a [Playground] file is accessed, it must be copied
from S3 to the server. This negatively impacts performance.

## <a name="persistent s3"></a>Using S3 or S3-compatible

To use [S3] (or a non-[AWS]<span></span> [S3]-compatible service) for persistent
storage, you need to obtain credentials and create a bucket.

If you want to use [Amazon Web Services], you would first sign up for
an [AWS] account, and go to the [S3 Console], click "Create Bucket,"
and pick a name. If your site is at docassemble.example.com, a good
name for the bucket is `docassemble-example-com`. (Client software
will have trouble accessing your bucket if it contains `.`
characters.)  Under "Region," pick the region nearest you.
Then you need to obtain an access key and a secret access key for
[S3]. To obtain these credentials, go to [IAM Console] and create a
user with "programmatic access."  Under "Attach existing policies
directly," find the policy called `AmazonS3FullAccess` and attach it
to the user.

When you run your **docassemble** [Docker] container, set the
[configuration options]<span></span> [`S3BUCKET`], [`S3ACCESSKEY`],
[`S3SECRETACCESSKEY`], and [`S3REGION`]. For example, you might use
an `env.list` file such as:

{% highlight text %}
DAHOSTNAME=interviews.example.com
S3ENABLE=true
S3BUCKET=interviews-example-com
S3ACCESSKEY=YERWERGDFSGERGSDFGSW
S3SECRETACCESSKEY=WERWR36dddeg3udjfRT1+rweRTHRTookiMVASDAS
S3REGION=us-east-2
TIMEZONE=America/New_York
USEHTTPS=true
EC2=true
USELETSENCRYPT=true
LETSENCRYPTEMAIL=dev@example.com
{% endhighlight %}

If you are using an [S3]-compatible object storage service, you will
need to set [`S3ENDPOINTURL`] to the URL endpoint of your service,
which you can find in the service's documentation or in your account
settings. You likely will not need to set [`S3REGION`] unless the
service supports the "region" concept.

For example, if you are using the [Digital Ocean] Spaces service using
the San Francisco datacenter, your `env.list` file might contain:

{% highlight text %}
S3ENABLE=true
S3BUCKET=interviews-example-com
S3ACCESSKEY=YERWERGDFSGERGSDFGSW
S3SECRETACCESSKEY=WERWR36dddeg3udjfRT1+rweRTHRTookiMVASDAS
S3ENDPOINTURL=https://sfo3.digitaloceanspaces.com
{% endhighlight %}

Keep in mind that the secret access keys that you include in your
environment variables will become available to all developers who use
your **docassemble** server, since they will be stored in the
configuration file.

Note that if you run **docassemble** on [EC2], you can launch your
[EC2] instances with an [IAM] role that allows **docassemble** to
access to an [S3] bucket without the necessity of setting
[`S3ACCESSKEY`] and [`S3SECRETACCESSKEY`]. In this case, the only
environment variable you need to pass is [`S3BUCKET`].

If you are using [AWS] and you want to limit access to a particular
bucket, you do not have to use the `AmazonS3FullAccess` policy when
obtaining [S3] credentials. Instead, you can create your own policy
with the following definition:

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

When setting up your [S3] bucket, you should consider setting up a
backup mechanism using the [S3] provider's site. When uploaded files
are stored in [S3], **docassemble** does not include those files in
its rotating backups.

## <a name="persistent azure"></a>Using Microsoft Azure

Using [Microsoft Azure] is very similar to using [S3]. From the
[Azure Portal] dashboard, search for "Storage accounts" in the
"Resources."  Click "Add" to create a new storage account. Under
"Account kind," choose "BlobStorage."  Under "Access tier," you can
choose either "Cool" or "Hot," but you may have to pay more for "Hot."

Once the storage account is created, go into your "Blobs" service in
the storage account and click "+ Container" to add a new container.
Set the "Access type" to "Private."  The name of the container
corresponds with the [`AZURECONTAINER`] environment variable. Back at
the storage account, click "Access keys."  The "Storage account name"
corresponds with the environment variable [`AZUREACCOUNTNAME`]. The
"key1" corresponds with the [`AZUREACCOUNTKEY`] environment variable.
(You can also use "key2."). For example, you might use an `env.list`
file such as:

{% highlight text %}
DAHOSTNAME=interviews.example.com
AZUREENABLE=true
AZUREACCOUNTNAME=exampledotcom
AZUREACCOUNTKEY=98f89asdfjwew/YosdfojweafASDFErgergDFGsergagaweWRTIQgqERGs243rergE4534tERgEFBDRGferEEB==
AZURECONTAINER=interviews-example-com
TIMEZONE=America/New_York
USEHTTPS=true
USELETSENCRYPT=true
LETSENCRYPTEMAIL=dev@example.com
{% endhighlight %}

If you enable both [S3](#persistent s3) and
[Azure blob storage](#persistent azure), only [S3] will be used.

When setting up Azure blob storage, you should consider setting up a
backup mechanism in Azure. When uploaded files are stored in Azure
blob storage, **docassemble** does not include those files in its
rotating backups.

## <a name="persistent"></a>Using persistent volumes

To run **docassemble** in a [single-server arrangement] in such a way
that the [configuration], the [Playground] files, the uploaded files,
and other data persist after the [Docker] container is removed or
updated, run the image as follows:

{% highlight bash %}
docker run --env-file=env.list \
-v dabackup:/usr/share/docassemble/backup \
-d -p 80:80 -p 443:443 --restart always --stop-timeout 600 \
jhpyle/docassemble
{% endhighlight %}

where `--env-file=env.list` is an optional parameter that refers to a
file `env.list` containing environment variables for the
configuration. A [template for the `env.list` file] is included in
distribution.

An advantage of using persistent volumes is that you can completely
replace the **docassemble** container and rebuild it from scratch, and
when you `run` the `jhpyle/docassemble` image again, docassemble will
keep running where it left off.

If you are using [HTTPS] with your own certificates (as opposed to
using [Let's Encrypt]), or you need to provide other SSL certificates
to **docassemble** (for example, for PostgreSQL and/or Redis
encryption) you can use a persistent volume to provide the
certificates to the [Docker] container; add `-v
dacerts:/usr/share/docassemble/certs` to your [`docker run`]
command. For more information on creating a persistent volume for SSL
certificates, see [below](#own certificates).

To see what volumes exist on your [Docker] system, you can run:

{% highlight bash %}
docker volume ls
{% endhighlight %}

A volume will be created when you run `docker run` with the `-v`
option. For example, the `docker run` command above specified `-v
dabackup:/usr/share/docassemble/backup`. If a volume called `dabackup`
does not already exist, it will be created, and the
`jhpyle/docassemble` container will initialize its contents. The
`dabackup` volume will be associated with the directory
`/usr/share/docassemble/backup` inside the container. The `docker
volume ls` command can be used to list the files inside of a
volume. `docker cp` can be used to copy files from the host to the
`/usr/share/docassemble/backup` folder.

You might want to initialize a volume before starting your
**docassemble** server, for example in order to provide certificates
to **docassemble**. For example, to create a volume called `dacerts`,
you can `docker run` the minimal `busybox` container with the volume
mounted to `/data`:

{% highlight bash %}
docker run -v dacerts:/data --name deleteme busybox true
{% endhighlight %}

Then you can use `docker cp` to copy files to it:

{% highlight bash %}
docker cp redis.crt deleteme:/data/
docker cp redis.key deleteme:/data/
{% endhighlight %}

Then you can delete the container, as it is no longer needed:

Now delete the [BusyBox] container. (The volume `dacerts` will not be
deleted.)

{% highlight bash %}
docker rm deleteme
{% endhighlight %}

Now that the `dacerts` volume has already been created on the host, if
you do:

{% highlight bash %}
docker run --env-file=env.list \
-v dabackup:/usr/share/docassemble/backup \
-v dacerts:/usr/share/docassemble/certs \
-d -p 80:80 -p 443:443 --restart always --stop-timeout 600 \
jhpyle/docassemble
{% endhighlight %}

then the directory `/usr/share/docassemble/certs` will already be
prepopulated when **docassemble** starts.

If you want to see the files in the `dacerts` volume, do:

{% highlight bash %}
docker volume ls dacerts
{% endhighlight %}

If you want to delete the `dacerts` volume, do:

{% highlight bash %}
docker volume rm dacerts
{% endhighlight %}

To delete all of the volumes, do:

{% highlight bash %}
docker volume rm $(docker volume ls -qf dangling=true)
{% endhighlight %}

[Docker volumes] are powerful but complicated. If you want to use
them, you can read about them in the Docker documentation and other
places on the internet.

It is recommended that you do not create [Docker volumes] for
directories other than `/usr/share/docassemble/certs` and
`/usr/share/docassemble/backup`. If you try to mount other directories
as volumes, you might experience hard-to-debug problems. Depending on
the architecture, the directories might cause the container to
malfunction because certain file system features that the software
depends on are not available. If you create a volume for a directory,
your directory will supplant the directory that is present in the
Docker image, so unless you populate the directory with the same files
that the image provides, your **docassemble** server may be
non-functional.

Ultimately, the better [data storage] solution is to use cloud storage
([S3](#persistent s3), [Azure blob storage](#persistent azure)) because:

1. [S3](#persistent s3) and [Azure blob storage](#persistent azure)
   make scaling easier. They are the "cloud" way of storing
   persistent data, at least until cloud-based network file systems
   become more robust.
2. It is easier to upgrade your virtual machines to the latest
   software and operating system if you can just destroy them and
   recreate them, rather than running update scripts. If your
   persistent data is stored in the cloud, you can destroy and
   recreate virtual machines at will, without ever having to worry
   about copying your data on and off the machines.

However, you can get around the second problem by using [`docker
volume create`] to put your [Docker volume] on a separate drive. That
way, you could remove the virtual machine that runs the application,
along with its primary drive, without affecting the drive with the
**docassemble** data.

## <a name="password loss"></a>If you lose your admin password

If you cannot log into your **docassemble** server because you forgot
the password of your account with `admin` privileges, it is possible
to go in through the back end to change the password. This is
complicated by the fact that passwords are encrypted.

In order to change the password of your user with `admin` privileges,
you will need to know the password of another account on your server,
even if it is an unprivileged account. If you don't know the password
of any other account, you can register as a new user.

The following instructions assume that you have not configured
**docassemble** to use an external SQL database, and you are using the
default configuration, which is that there is a SQL database inside
the Docker container named `docassemble`.

Use `docker exec` to get a command line inside your container. (If you
don't know how to do this, see the [troubleshooting] section.)

Then do:

{% highlight text %}
# su postgres
$ psql docassemble
{% endhighlight %}

Now you should have a `#` prompt inside of `psql`, so that you can
issue SQL commands.

First, find out the user ID of the user whose password you know, as
well as the user ID of the user with administrative privileges whose
password you want to change.

{% highlight text %}
# select id, email from "user"
{% endhighlight %}

Then, get the encrypted password of that user (assuming the ID is
`15`):

{% highlight text %}
# select password from user_auth where user_id=15;
{% endhighlight %}

Now that you know the encrypted version of the known password, you can
change the password of the admin user to that encrypted password
(assuming the ID of the user with `admin` privileges is `1`).

{% highlight text %}
# update user_auth set password='$2b$12$B5WscXrNatMg/0mMGU63VuY8NPN6IFY7MmhFocKGGU86OXFryLuDi' where id=1;
{% endhighlight %}

Now, you should be able to log in as the user with `admin` privileges
using the known password.

Note that the passwords are encrypted using the [`secretkey`] as a
"salt," so the encrypted version of a password will vary from server
to server.

## <a name="recovery"></a>Recovery from backup files

When you are using [data storage], you can do `docker stop -t 600` on
a container, followed by `docker rm`, and then re-run your original
`docker run` command, and when the system starts again, it will be in
the same place it was before, with the same uploaded files, the same
SQL database.

During the `docker stop` process, application data are saved into
files and directories in the [data storage] area. During `docker run`
(and `docker start` as well), application data are restored from the
[data storage] area before the server attempts to start. Included in
the application data is a the list of Python packages installed on
your system; when the server starts, `pip` will be used to install the
same list of packages.

This backup-on-shutdown/restore-on-startup feature is very powerful
because it means you can shut down, delete your Docker container, pull
a new Docker image, and then re-run `docker run`, and all of your
application data and Python packages will be restored. Between the
old Docker image and the new Docker image, the versions of the
operating system, PostgreSQL, and Python might have changed, but the
restore process will adjust for this.

However, if your server has an unsafe shutdown, the files in the [data
storage] area might be corrupted. They might also be missing or very
old (dating from the last time there was a safe shutdown). If this
happens, not all is lost, because you can restore from one of the
daily backup snapshots.

If you are using [S3](#persistent s3) or [Azure blob
storage](#persistent azure), the files and directories that are saved
during the shutdown process are:

* `postgres` - a folder containing a "dump" of each database hosted by
  the [PostgreSQL] server. Usually the operative file is called
  `docassemble`, for the database called `docassemble`. If you point
  your server to an external database using the [`db` section] of your
  [Configuration], this is not applicable. The backup file will
  exist, but it will be an empty database.
* `redis.rdb` - a file containing a backup of the [Redis] database.
  If you point your server to an external [Redis] database using a
  [`redis`] directive in your [Configuration], this is not
  applicable. The `redis.rdb` file will exist, but it will be an
  empty database.
* `log` - a folder containing **docassemble** log files.
* `nginxlogs` - a folder containing the logs for [NGINX]. If you are
  using Apache, the relevant folder is `apachelogs`. This is not
  applicable unless the `CONTAINERROLE` is `all`.

The `files` folder, the `config.yml` file, and the
`letsencrypt.tar.gz` (if Let's Encrypt is used) are important for
restoring the system on startup, but they are always up-to-date; they
are not copied from the server during the shutdown process. So even
if you have an unsafe shutdown, you will have up-to-date versions of
`files`, `config.yml`, and `letsencrypt.tar.gz`.

If you are not using [S3](#persistent s3) or [Azure blob
storage](#persistent azure), then during a safe shutdown process,
application data is saved into the following files and folders:

* `/usr/share/docassemble/backup/postgres` - a folder containing a
  "dump" of each database hosted by the [PostgreSQL] server. Usually
  the operative file is called `docassemble`, for the database called
  `docassemble`. If you point your server to an external database
  using the [`db` section] of your [Configuration], this is not
  applicable. The backup file will exist, but it will be an empty
  database.
* `/usr/share/docassemble/backup/redis.rdb` - a file containing a
  backup of the [Redis] database. If you point your server to an
  external [Redis] database using a [`redis`] directive in your
  [Configuration], this is not applicable. The `redis.rdb` file will
  exist, but it will be an empty database.
* `/usr/share/docassemble/backup/files` - a directory containing all
  of the stored files in your system (document uploads, assembled
  documents, ZIP files for installed packages, etc.). If [`backup file
  storage`] in the [Configuration] is set to `false`, then this will
  not exist.
* `/usr/share/docassemble/backup/log` - a folder containing
  **docassemble** log files.
* `/usr/share/docassemble/backup/nginxlogs` - a folder containing the
  logs for [NGINX]. If you are using Apache, the relevant folder is
  `/usr/share/docassemble/backup/apachelogs`. This is not applicable
  unless the `CONTAINERROLE` is `all`.
* `/usr/share/docassemble/backup/config/config.yml` - a file
  containing the Configuration of your system.

The file `/usr/share/docassemble/backup/letsencrypt.tar.gz` is
important for restoring the system (if Let's Encrypt is used), but it
is always up-to-date; it is not copied from the server during the
shutdown process.

Whenever a **docassemble** container starts up, the [PostgreSQL]
database in `postgres/docassemble` is used to restore
**docassemble**'s SQL database. The `redis.rdb` file is used to
restore the Redis database. These files are created during the
shutdown process. It is important that the shutdown process happens
gracefully, because otherwise these files will not be complete.

As protection against the risk of an unsafe shutdown (as well as the
risk of the accidental deletion of data), **docassemble** maintains a
daily rotating backup. The daily backup is created whenever the daily
cron job runs (which is typically around 6:00 in the morning).

If you are using [S3](#persistent s3) or [Azure blob
storage](#persistent azure), these backups are in the `backup` folder
in the cloud storage. There is a subfolder in the `backup` folder for
each container that has used the cloud storage area. The subfolder
names come from the internal hostnames of containers. In a
[multi-server arrangement], you will see several subfolders. You may
also see several subfolders if you have called `docker run` multiple
times. Within a subfolder for a container, there are subfolders for
each day for which there is a backup. The folders are in the format
`MM-DD` where `MM` is the month and `DD` is the day of the month. If
you want to restore your system to a snapshot of where it was when a
daily backup was made, you will need to shut down your server(s) with
`docker stop -t 600` if it is still running. Then you will need to
copy files from the daily backup location to the places where they
will be used when the system starts up again. In particular, you will
copy the following out of the daily backup folder:

* `config/config.yml` to `config.yml` in the root of the cloud storage.
* `files` to `files` in the root of the cloud storage.
* `postgres` to `postgres` in the root of the cloud storage.
* `redis.rdb` to `redis.rdb` in the root of the cloud storage.
* `log` to `log` in the root of the cloud storage.

Copying `log` is optional. The contents of log files are not critical
to the functionality of the systems.

Note that when using [S3](#persistent s3) or [Azure blob
storage](#persistent azure), file storage (uploaded files, assembled
documents) are already in the cloud, so they are not backed up to the
`backup` folder. If you want a backup mechanism for these files, you
can enable it using [S3] or [Azure blob storage] site.

If you are not using [S3](#persistent s3) or [Azure blob
storage](#persistent azure), the disaster recovery backup files are in
folders named `/usr/share/docassemble/backup/MM-DD` where `MM` is the
month and `DD` is the day the backup was made. If you want to restore
your system to a snapshot of where it was when a daily backup was
made, you will first need to shut down your server with `docker stop
-t 600` if it is still running. Then you will need to copy files from
the daily backup location to the places where they will be used when
the system starts up again. In particular, you will copy the
following out of the daily backup folder:

* the `config/config.yml` file to `/usr/share/docassemble/backup/config.yml`
* the `files` folder to `/usr/share/docassemble/backup/files`
* the `postgres` folder to `/usr/share/docassemble/backup/postgres`
* the `redis.rdb` file to `/usr/share/docassemble/backup/redis.rdb`
* the `log` folder to `/usr/share/docassemble/backup/log`

Copying `log` is optional. The contents of log files are not critical
to the functionality of the systems.

After copying these files into place, you can start your server(s)
with `docker run` (using the same parameters you originally used) or
`docker start`.

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
[`CONTAINERROLE`], which is passed to the container at startup. In a
single-server arrangement ([`CONTAINERROLE`] = `all`, or left
undefined), the container runs all of the services (except the log
message aggregator, which is not necessary in the case of a
single-server arrangement).

You can run **docassemble** in a [multi-server arrangement] using
[Docker] by running the **docassemble** image on different hosts using
different [configuration options].

In a multi-server arrangement, you can have one machine run SQL,
another machine run [Redis] and [RabbitMQ], and any number of machines
run web servers and [Celery] nodes. You can decide how to allocate
services to different machines. For example, you might want to run
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

If you are only using a single Docker container to run the
**docassemble** web application and [Celery], then even if you are
using an external SQL server, external [Redis] server, and external
[RabbitMQ] server, you can keep the `CONTAINERROLE` as `all` (or
undefined).

## <a name="ports"></a>Port opening

Note that for every service that a [Docker] container provides,
appropriate ports need to be forwarded from the [Docker] host machine
to the container.

* Regardless of the [`CONTAINERROLE`], port 9001 needs to be forwarded
  so that the container can be controlled via [supervisor].
* If [`CONTAINERROLE`] includes `sql`: forward port 5432 ([PostgreSQL])
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
--env CONTAINERROLE=sql:redis \
...
-d -p 5432:5432 -p 6379:6379 -p 9001:9001 \
--restart always --stop-timeout 600 jhpyle/docassemble
{% endhighlight %}

{% highlight bash %}
docker run \
--env CONTAINERROLE=web:celery \
...
-d -p 80:80 -p 443:443 -p 9001:9001 \
--restart always --stop-timeout 600 jhpyle/docassemble
{% endhighlight %}

Note that [Docker] will fail if any of these ports is already in use.
For example, many Linux distributions run a mail transport agent on
port 25 by default; you will have to stop that service in order to
start [Docker] with `-p 25:25`. For example, on [Amazon Linux] you
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
system. This directory contains the configuration, SSL certificates,
[Python virtual environment], and uploaded files. However, network
file systems present problems.

A preferable way to share files is with [Amazon S3] or
[Azure blob storage], which **docassemble** supports. See the
[using S3] and [using Azure blob storage] sections for instructions on
setting this up.

## <a name="config file"></a>Configuration file

Note that when you use the cloud ([S3](#persistent s3) or
[Azure blob storage](#persistent azure)) for [data storage],
**docassemble** will copy the `config.yml` file out of the cloud on
startup, and save `config.yml` to the cloud whenever the configuration
is modified.

This means that as long as there is a `config.yml` file in the cloud
with the configuration you want, you can start **docassemble**
containers without specifying a lot of [configuration options]; you
simply have to refer to your cloud storage bucket/container, and
**docassemble** will take it from there. For example, to run a
central server, you can do:

{% highlight bash %}
docker run \
--env CONTAINERROLE=sql:redis:rabbitmq:log:cron:mail \
--env S3BUCKET=docassemble-example-com \
--env S3ACCESSKEY=FWIEJFIJIDGISEJFWOEF \
--env S3SECRETACCESSKEY=RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG \
-d -p 80:8080 -p 25:25 -p 465:465 -p 5432:5432 -p 514:514 \
-p 6379:6379 -p 4369:4369 -p 5671:5671 \
-p 5672:5672 -p 25672:25672 -p 9001:9001 \
--restart always --stop-timeout 600 jhpyle/docassemble
{% endhighlight %}

To run an application server, you can do:

{% highlight bash %}
docker run \
--env CONTAINERROLE=web:celery \
--env S3BUCKET=docassemble-example-com \
--env S3ACCESSKEY=FWIEJFIJIDGISEJFWOEF \
--env S3SECRETACCESSKEY=RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG \
-d -p 80:80 -p 443:443 -p 9001:9001 \
--restart always --stop-timeout 600 jhpyle/docassemble
{% endhighlight %}

# <a name="Encryption"></a>Encrypting communications

## <a name="https"></a>Using HTTPS

If you are running **docassemble** on [EC2], the easiest way to enable
HTTPS support is to set up an [Application Load Balancer] that accepts
connections in HTTPS format and forwards them to the web servers in
HTTP format. In this configuration [Amazon] takes care of creating
and hosting the necessary SSL certificates.

If you are not using a [load balancer], you can use HTTPS either by
setting up [Let's Encrypt] or by providing your own certificates.

### <a name="letsencrypt"></a>With Let's Encrypt

If you are running **docassemble** in a [single-server arrangement],
or in a [multi-server arrangement] with only one web server, you can
use [Let's Encrypt] to enable [HTTPS]. If you have more than one web
server, you can enable encryption [without Let's Encrypt] by
installing your own certificates.

To use [Let's Encrypt], set the following environment variables in
your task definition or `env.list` file:

* `USELETSENCRYPT`: set this to `true`.
* `LETSENCRYPTEMAIL`: [Let's Encrypt] requires an e-mail address, which
  it will use to get in touch with you about renewing the SSL certificates.
* `DAHOSTNAME`: set this to the hostname that users will use to get to
  the web application. [Let's Encrypt] needs this in order to verify
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
be run, which will change the [NGINX] configuration in order to use the
appropriate SSL certificates. When the server is later restarted,
the `letsencrypt renew` command will be run, which will refresh the
certificates if they are within 30 days of expiring.

In addition, a [script] will run on a daily basis to attempt to renew
the certificates.

If you are using a [multi-server arrangement] with a single web
server, you need to run the `cron` role on the same server that runs
the `web` role. If you use the [e-mail receiving] feature with
[TLS encryption], the `mail` role also has to share the server with
the `web` and `cron` roles.

### <a name="own certificates"></a>Using your own certificates

If you do not want to use Let's Encrypt to support HTTPS, or you have
other SSL certificates that your server needs to use, you can pass
your certificates to **docassemble**.

Using your own SSL certificates with [Docker] requires that your SSL
certificates reside within each container. There are several ways to
get your certificates into the container:

* Use [S3](#persistent s3) or [Azure blob storage](#persistent azure)
  and upload the certificates to `certs/` in your bucket/container.
* [Build your own private image] in which your SSL certificates are
  placed in `Docker/ssl`. During the build process, these files will
  be copied into `/usr/share/docassemble/certs`.
* Use [persistent volumes] and copy the SSL certificate files
  into the volume for `/usr/share/docassemble/certs` before starting
  the container.

The default [NGINX] configuration file expects SSL certificates to be
located in the following files:

{% highlight text %}
ssl_certificate /etc/ssl/docassemble/nginx.crt;
ssl_certificate_key /etc/ssl/docassemble/nginx.key;
{% endhighlight %}

The meaning of these files is as follows:

* `nginx.crt`: this file is generated by your certificate
  authority when you submit a certificate signing request.
* `nginx.key`: this file is generated at the time you create
  your certificate signing request.

Other certificate files that **docassemble** uses include:

* `exim.crt` - certificate for the Exim mail daemon
* `exim.key` - certificate key for Exim mail daemon
* `redis.crt` - certificate for an external Redis server
* `redis.key` - certificate key for an external Redis server
* `redis_ca.crt` - certificate authority certificate for an external
  Redis server

In addition, if your [`db`] configuration refers to an `ssl cert`,
`ssl key`, or `ssl root cert`, these need to be the names of files
that are present in certificate storage.

In order to make sure that these certificates are replicated on every
web server, the [supervisor] will run the
`docassemble.webapp.install_certs` module before starting the web
server.

If you are using [S3](#persistent s3) or [Azure blob storage](#persistent azure),
this module will copy the files from the `certs/` prefix in your
bucket/container to `/etc/ssl/docassemble`. You can use the [S3
Console] or the [Azure Portal] to create a folder called `certs` and
upload your certificate files into that folder.

If you are not using [S3](#persistent s3) or [Azure blob storage](#persistent azure), the
`docassemble.webapp.install_certs` module will copy the files from
`/usr/share/docassemble/certs` to `/etc/ssl/docassemble`.

There are two ways that you can put your own certificate files into
the `/usr/share/docassemble/certs` directory. The first way is to
[create your own Docker image] of **docassemble** and put your
certificates into the `Docker/ssl` directory. The contents of this
directory are copied into `/usr/share/docassemble/certs` during the
build process.

The second way is to use [persistent volumes]. If you have a
persistent volume for the directory `/usr/share/docassemble/certs`,
you can copy the SSL certificate files into that directory before
starting the container.

If you are starting a new server using a [persistent volume], you can
set up your own certificates as follows.

Create an `env.list` file like the following:

{% highlight text %}
DAHOSTNAME=myserver.example.com
TIMEZONE=America/New_York
USEHTTPS=true
{% endhighlight %}

(Of course, you may also need additional environment variables, such
as `EC2`, depending on your setup.)

Create a docker volume called `dacerts` using a temporary container
based on the minimal [BusyBox] image.

{% highlight bash %}
docker run -v dacerts:/data --name deleteme busybox true
{% endhighlight %}

Now copy your SSL certificate files to the volume.

{% highlight bash %}
docker cp nginx.crt deleteme:/data/
docker cp nginx.key deleteme:/data/
{% endhighlight %}

You may want to copy other certificates as well, for example for
PostgreSQL or Redis.

Now delete the [BusyBox] container. (Your volume will not be
deleted.)

{% highlight bash %}
docker rm deleteme
{% endhighlight %}

Now start your **docassemble** container using the `dacerts` volume
mounted to `/usr/share/docassemble/certs`:

{% highlight bash %}
docker run \
  --restart always \
  --stop-timeout 600 \
  --env-file=env.list \
  -v dabackup:/usr/share/docassemble/backup \
  -v dacerts:/usr/share/docassemble/certs \
  -d -p 80:80 -p 443:443 jhpyle/docassemble
{% endhighlight %}

When it comes time to update your NGINX certificate files, save the
new certificates as `nginx.crt` and `nginx.key`, and then do:

{% highlight bash %}
docker cp nginx.crt a3970318cb38:/usr/share/docassemble/certs/
docker cp nginx.key a3970318cb38:/usr/share/docassemble/certs/
{% endhighlight %}

replacing `a3970318cb38` with whatever the ID or name of your
container is.

Then restart your container:

{% highlight bash %}
docker stop -t 600 a3970318cb38
docker start a3970318cb38
{% endhighlight %}

This last step is important; the location
`/usr/share/docassemble/certs/` is not a working directory, but a
staging area. If the server is running, changing the files in that
directory will not change the certificates that **docassemble**
uses. You need to stop and start the container for
`docassemble.webapp.install_certs` to copy the files to the correct
working directories and for the services to restart using the new
certificates.

If you want to use different filesystem or cloud locations, the
`docassemble.webapp.install_certs` module can be configured to use
different locations. See the [configuration] variable [`certs`].

## <a name="tls"></a>Using TLS for incoming e-mail

If you use the [e-mail receiving] feature, you can use [TLS] to
encrypt incoming e-mail communications. By default, **docassemble**
will install self-signed certificates into the [Exim] configuration,
but for best results you should use certificates that match your
[`incoming mail domain`].

If you are using [Let's Encrypt] to obtain your [HTTPS] certificates
in a [single-server arrangement], then **docassemble** will use your
[Let's Encrypt] certificates for [Exim].

However, if you are running your `mail` server as part of a dedicated
backend server that does not include `web`, you will need to create
and install your own certificates. In addition, if your
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

# <a name="forwarding"></a>Using a web server and a reverse proxy

Instead of having users access your **docassemble** interviews at
https://da.foobar.com, where the DNS for `da.foobar.com` points to
your **docassemble** server, and SSL certificates are obtained by your
**docassemble** container, you can have your users access your
**docassemble** interviews at https://foobar.com/da, where the DNS for
`foobar.com` points to a web server you operate, and that web server
acts as a go-between between the user's web browser and the
**docassemble** server. The **docassemble** server may operate on a
same machine that runs your web server, or a different machine. The
machine that operates the **docassemble** server does not have to be
exposed to the internet; it might be on a local network, so long as
the web server can access it.

You should use this deployment strategy if you wish to [embed] a
**docassemble** interview into another site using an [`<iframe>`]. In
the past, using an [`<iframe>`] was a convenient way to allow HTML
content from a different server to appear inside your server. However,
in recent years, web browsers have become more restrictive about
[Cross-Origin Resource Sharing]. Browsers like Safari will block
[`<iframe>`] content that stores information in the user's browser if
the URL of the [`<iframe>`] uses a hostname that is different from the
hostname in the browser location bar.

The following example illustrates how to do this. Your situation will
probably be different, but this example will still help you figure out
how to configure your system.

## <a name="forwarding nginx"></a>Example using NGINX

The example will demonstrate how to run **docassemble** using [Docker]
on an Ubuntu 22.04 server running in the cloud. The machine that runs
[Docker] will also run the [NGINX] web browser. [NGINX] will be
configured to use encryption and it will listen on ports 80 and 443.
The web server will be accessible at `https://justice.example.com` and
will serve resources other than **docassemble**. The **docassemble**
resources will be accessible at `https://justice.example.com/da`.
[Docker] will run on the machine and will listen on ports 8080
and 8050. The web server will accept HTTPS requests at `/da` and
forward thema as HTTP requests to port 8080. The SSL certificate will
be installed on the Ubuntu server, and the [Docker] container will run
an HTTP server. [Docker] will be controlled by the user account
`ubuntu`, which is assumed to have [sudo] privileges.

This example uses only one machine, but if you want to have a separate
machine for your web browser and a separate machine for running
**docassemble**, it is easy to set that up.

If you want to follow along with this example, make sure that you have
purchased a domain name from a domain registrar and you have set up a
[CNAME record] or an [A record] in your [DNS] configuration that
associates a hostname with your server. Also make sure that the
firewall protecting the machine has ports 80 (HTTP) and 443 (HTTPS)
open.

In this example, we own the domain `example.com` domain and we have
set up an `A` record in our [DNS] configuration that associates
`justice.example.com` with the IP address of our server.

First, let's install [NGINX], [Let's Encrypt] (the [certbot] utility),
and [Docker] on the Ubuntu server. We use an [SSH client] to log in to
the server as the user `ubuntu`. Then we run some commands on the
command line:

{% highlight bash %}
sudo apt -y update
sudo apt -y install snapd nginx docker.io
sudo snap install --classic certbot
sudo usermod -a -G docker ubuntu
{% endhighlight %}

The last command changes the user privileges of the `ubuntu` user.
For these changes to take effect, you need to log out and log in again.
(E.g., exit the [ssh] session and start a new one.)

At this point, your web server should be running and should be visible
from the internet. In our example, we can visit
`http://justice.example.com` and we are greeted by a page that
says "Welcome to nginx!"

This is good, but we want to access our server using `https://`, not
`http://`. We will encounter a lot of problems if our connection runs
on `http://`. In order to enable HTTPS, we can run
[`certbot`]. [`certbot`] is an application that automates the process
of obtaining SSL certificates from [Let's Encrypt] and modifying the
web browser configuration files so that they use these new
certificates.

To run `certbot`, do:

{% highlight bash %}
sudo certbot --nginx
{% endhighlight %}

Answer all of the prompts that appear. It is particularly important
that you provide the correct domain name. In our example, we entered
`justice.example.com`.

Note that if you are using [AWS] and you are given a hostname such as
`ec2-54-213-142-150.us-west-2.compute.amazonaws.com`, [certbot] will
not issue a certificate for this hostname. You must purchase a real
hostname of your own from a domain name registrar.

It is also important that you provide a good e-mail address to
[`certbot`]. You will get an e-mail from [Let's Encrypt] if your
certificate is about to expire.

Upon completion, `certbot` shows the message "Congratulations! You
have successfully enabled HTTPS on https://justice.example.com."

Now, if you visit your web site again, you will see it redirects your
browser to the `https://` version of the site. In the browser you can
see a padlock next to the location bar, indicating that the web site
uses encryption.

Now that you have your web server running, you can install
**docassemble**. (In this example, we will install it on the same
server that is running [NGINX], but you can also use a different
machine.) First you need to create a short text file called `env.list`
that contains some configuration options for **docassemble**.

{% highlight bash %}
nano env.list
{% endhighlight %}

Set the contents of `env.list` to:

{% highlight text %}
BEHINDHTTPSLOADBALANCER=true
POSTURLROOT=/da/
DAEXPOSEWEBSOCKETS=true
{% endhighlight %}

Inside of `nano`, you can save the file by typing Ctrl-s and exit by
typing Ctrl-x.

The `POSTURLROOT` variable, which is set to `/da/`, indicates the
path after the domain at which **docassemble** can be accessed. The
[NGINX] web server will be able to provide other resources at other
paths, but `/da/` will be reserved for the exclusive use of
**docassemble**. The beginning slash and the trailing slash are both
necessary.

Setting [`DAEXPOSEWEBSOCKETS`] to `true` means that the [WebSocket]
server running inside the container (the [supervisor] process called
`websockets`) will expose port 5000 to the external IP address rather
than port 5000 of 127.0.0.1, so that the web server on the host can
act as a proxy server for it.

Now, let's download, install, and run **docassemble**.

{% highlight bash %}
docker run --env-file=env.list -v dabackup:/usr/share/docassemble/backup -d -p 8080:80 -p 8050:5000 jhpyle/docassemble
{% endhighlight %}

The option `-p 8080:80` means that port 8080 on the Ubuntu machine
will be mapped to port 80 within the [Docker] container. The option
`-p 8050:5000` means that the web sockets port of the container should
be accessible on port 8050 of the host, so that the web server on the
host can tunnel traffic to it directly. Note that ports 8080 and 8050
are not available from the internet (unless you configured your
firewall to allow such access); what is important is that they are
available to the [NGINX] web server that is running on the host.

Now, let's edit the NGINX configuration so that the **docassemble**
application is accessible through the NGINX web server.

{% highlight bash %}
nano /etc/nginx/sites-available/default
{% endhighlight %}

Scroll down to the second `server {` configuration. Look for a line
that looks like this:

{% highlight text %}
server_name justice.example.com; # managed by Certbot
{% endhighlight %}

After this line, put in the following:

{% highlight text %}
location /da/ws {
    include proxy_params;
    proxy_pass http://localhost:8050;
}

location /da/ws/socket.io {
    include proxy_params;
    proxy_http_version 1.1;
    proxy_buffering off;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
    proxy_pass http://localhost:8050/socket.io;
}

location /da {
    include proxy_params;
    proxy_pass http://localhost:8080;
}
{% endhighlight %}

The last `location` configuration is the most important setting. The
others support websockets connections, which support the [Live Help]
feature.

Next, restart [NGINX] so that it uses the new configuration.

{% highlight text %}
sudo systemctl restart nginx
{% endhighlight %}

Now, we can access the **docassemble** server at
`https://justice.example.com/da`.

Next, we can build a web site (using non-**docassemble** tools) and
operate it on the [NGINX] web server running at
https://justice.example.com. Any URL that does not start with `/da`
will be handled by [NGINX] in the ordinary fashion.

If we wanted to embed a **docassemble** interview into a page of this
web site using an [`<iframe>`], there would be no [CORS] issues
because from the web browser's perspective, **docassemble** is just
another page on the https://justice.example.com web site.

## <a name="forwarding apache"></a>Example using Apache

If you prefer to use the [Apache] web server instead of [NGINX], you can
follow the above procedure, but instead of installing [NGINX], install
[Apache], run `sudo certbot --apache`.

Install the following [Apache] modules.

{% highlight bash %}
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel
sudo a2enmod headers
{% endhighlight %}

Edit the configuration file inside of `/etc/apache2/sites-enabled` so
that it contains:

{% highlight text %}
RewriteEngine On
RewriteCond %{REQUEST_URI}    ^/da/ws/socket.io     [NC]
RewriteCond %{QUERY_STRING}   transport=websocket   [NC]
RewriteRule /da/ws/(.*)  ws://localhost:8050/$1    [P,L]

ProxyPass /da/ws/ http://localhost:8050/
ProxyPassReverse /da/ws/ http://localhost:8050/

ProxyPass "/da"  "http://localhost:8080/da"
ProxyPassReverse "/da"  "http://localhost:8080/da"
RequestHeader set X-Forwarded-Proto "https"
{% endhighlight %}

Then restart the [Apache] server so that it uses the new
configuration.

{% highlight bash %}
sudo systemctl restart apache2
{% endhighlight %}

# <a name="build"></a>Creating your own Docker image

To create your own [Docker] image, first make sure [git] is
installed. If you are using [Docker Desktop] on a Windows PC or a Mac,
you may find that `git` is already installed, or the instructions may
explain how to run `git` using a Docker container.

If you are using Linux, installing git will look something like:

{% highlight bash %}
sudo apt -y install git
{% endhighlight %}

or

{% highlight bash %}
sudo yum -y install git
{% endhighlight %}

Then download docassemble, which consists of two images:

{% highlight bash %}
git clone https://github.com/jhpyle/docassemble-os
git clone {{ site.github.repository_url }}
{% endhighlight %}

Each of these repositories contains a `Dockerfile`. The
`jhpyle/docassemble` repository depends on
`jhpyle/docassemble-os`. (The `jhpyle/docassemble-os` repository is
separate because it contains operating system files and takes a long
time to build.

To make changes to the operating system or the operating system
packages that are installed inside the container, edit the
`Dockerfile` in the `jhpyle/docassemble-os` repository.

To make changes to the configuration of the **docassemble**
application, edit the following files in the `jhpyle/docassemble`
repository:

* <span></span>[`docassemble/Dockerfile`]: you may want to change the
  Python packages that are available when the server starts.
* <span></span>[`docassemble/Docker/config/config.yml.dist`]: you
  probably do not need to change this; it is a template that is
  updated based on the contents of the environment variables passed to
  [`docker run`]. Once your server is up and running you can change
  the rest of the configuration in the web application.
* <span></span>[`docassemble/Docker/initialize.sh`]: this script
  updates `config.yml` based on the environment variables; retrieves a
  new version of `config.yml` from [S3]/[Azure blob storage], if
  available; if [`CONTAINERROLE`] is not set to `web`, starts the
  [PostgreSQL] server and initializes the database if it does not
  exist; creates the tables in the database if they do not already
  exist; copies SSL certificates from [S3]/[Azure blob storage] or
  `/usr/share/docassemble/certs` if [S3]/[Azure blob storage] is not
  enabled; runs the [Let's Encrypt] utility if `USELETSENCRYPT` is
  `true` and the utility has not been run yet; and starts [NGINX] and
  other background tasks.
* <span></span>[`docassemble/Docker/config/nginx-http.dist`]:
  [NGINX] configuration file for handling HTTP requests.
* <span></span>[`docassemble/Docker/config/nginx-ssl.dist`]:
  [NGINX] configuration file for handling HTTPS requests.
* <span></span>[`docassemble/Docker/config/nginx-log.dist`]:
  [NGINX] configuration file for handling requests on port 8080.
  This is enabled if the [`CONTAINERROLE`] includes `log`.
* <span></span>[`docassemble/Docker/ssl/nginx.crt.orig`]: default SSL certificate for [NGINX].
* <span></span>[`docassemble/Docker/ssl/nginx.key.orig`]: default SSL certificate for [NGINX].
* <span></span>[`docassemble/Docker/ssl/exim.crt.orig`]: default SSL certificate for [Exim].
* <span></span>[`docassemble/Docker/ssl/exim.key.orig`]: default SSL certificate for [Exim].
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
* <span></span>[`docassemble/Docker/nginx.logrotate`]: This replaces the standard
  nginx logrotate configuration. It does not compress old log files,
  so that it is easier to view them in the web application.
* <span></span>[`docassemble/Docker/process-email.sh`]: This is a
  script that is run when an e-mail is received, if the
  [e-mail receiving] feature is configured.
* <span></span>[`docassemble/Docker/run-nginx.sh`]: This is a script
  that is run by [supervisor] to start the [NGINX] server.
* <span></span>[`docassemble/Docker/run-uwsgi.sh`]: This is a script
  that is run by [supervisor] to start the [uWSGI] server.
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
cd docassemble-os
docker build -t jhpyle/docassemble-os .
cd ../docassemble
docker build -t jhpyle/docassemble .
{% endhighlight %}

You can then run your image:

{% highlight bash %}
docker run -d -p 80:80 -p 443:443 --restart always --stop-timeout 600 jhpyle/docassemble
{% endhighlight %}

Or push it to [Docker Hub]:

{% highlight bash %}
docker tag yourdockerhubusername/mydocassemble jhpyle/docassemble
docker push yourdockerhubusername/mydocassemble
{% endhighlight %}

# <a name="arm"></a>ARM support

Using **docassemble** on the [ARM] architecture is considered
experimental. The known issues with [ARM] compatibility are:

* Google Chrome is not installed if the architecture is [ARM], so the
  `mmdc()` function will not work.
* For the same reason, you cannot use headless Chrome for web browser
  automation running inside the Docker container.

# <a name="upgrading"></a>Upgrading docassemble when using Docker

New versions of the **docassemble** software are published frequently.
Most changes only affect the [Python] code. You can upgrade the
**docassemble** [Python] packages by going to "Package Management"
from the menu and clicking the "Upgrade" button.

However, sometimes a "system upgrade" is necessary. This can happen
when changes are made to **docassemble**'s underlying operating system
files, or new versions of Python packages become incompatible with old
versions of operating system files, or **docassemble** requires a
newer version of Python than the version available in the operating
system. Performing a "system upgrade" requires stopping your
**docassemble** container and running `docker run` with a new version
of the **docassemble** image in order to start a new container based
on the new image.

Doing a system upgrade is only safe if you are already using a form
of [data storage]. If you aren't using a [Docker volume], [S3], or
[Azure blob storage], then your data will be lost if you attempt a
system upgrade.

Note that just as **docassemble** needs a "system upgrade" every once
in a while, the host operating system may also need to be upgraded. If
the operating system on the computer that runs Docker is old, it may
have trouble running the latest version of the Docker container. Also,
if you are running an old operating system on the host computer, you
may not have the latest security updates. Thus, before you do a system
upgrade, you should think about whether it is time to upgrade the host
operating system. If you are using the [S3] or [Azure blob storage]
form of [data storage], you can `docker stop` the Docker container,
terminate the host computer, create a new host computer with Docker
installed on it, change your [DNS] records to point to the new host
computer, and then do `docker run` on the new computer. If you are
using a [Docker volume] for data storage, you need to copy the [Docker
volume] from the old computer to the new computer, which can be a
time-consuming operation. (The steps are explained [below](#upgrading
starting).)

## <a name="upgrading basic"></a>Overview of a system upgrade

The basic steps of a system upgrade on a server are:

1. Safely shut down the **docassemble** server using `docker
   stop`. This will save your SQL database, Redis database, and files
   to [data storage].
2. Remove the old **docassemble** container and image by using `docker
   rm` and `docker rmi` to delete copies of the old **docassemble**
   containers and images.
3. Start a new container from the latest **docassemble** image using
   the same `docker run` command you ran when you created
   the original container.

When the new container starts up, it will retrieve the SQL database,
Redis database, and files from [data storage] and restore them into
the new container. Python packages you had installed on your old
container will be installed during the startup process. Your new
**docassemble** container will work just like the old one, except its
operating system will be upgraded and the **docassemble** software
will be fully upgraded.

## <a name="upgrading understanding docker"></a>Docker tools that are helpful when doing a system upgrade

If you are going to perform a system upgrade, it is important that you
understand some things about how Docker works.

[Docker] saves every image it uses to disk. So if you ran `docker run`
two years ago, [Docker] downloaded the image `jhpyle/docassemble` and
stored a copy of it on the disk. If you then run `docker run` today on
the `jhpyle/docassemble` image, [Docker] would use the downloaded
image from two years ago instead of downloading the latest image from
[Docker Hub].

The **docassemble** images take up a lot of disk space. One of the
easiest ways to run out of disk space when using **docassemble** is to
download too many copies of the `jhpyle/docassemble` image without
deleting old ones.

**docassemble** containers also take up disk space. If you have old
unused containers on your server, they will take up disk space and
also prevent you from deleting the images from which they were
created.

As long as you know that your data are backed up to [data storage],
you can clear up disk space and you don't need to worry about losing
your data. If you are using [S3] or [Azure blob storage] as your [data
storage] method, there is little to worry about; you can even delete
the host computer without worrying about losing your data. However, if
you are using a [Docker volume] for [data storage], you need to be
careful not to delete your volume (typically called `dabackup`) or the
host computer. If you want to switch to a different host computer, you
can copy the volume from one computer to another.

Here are some [Docker] commands you might want to use while doing a
system upgrade:

* `docker ps` will list all of the containers that are currently
  running.
* `docker stop -t 600 45034cf698b1` will stop the container with
  container ID `45034cf698b1` and it will give it ten minutes (600
  seconds) to shut down safely.
* `docker logs 45034cf698b1` will show the log of the container. This
  log is very high-level and limited, but it contains useful
  information about whether a container has shut down safely. There
  are more logs available inside the container itself; see
  [troubleshooting] for instructions on accessing them.
* `docker ps -a` will list all of the containers on the server,
  whether they are running or not.
* `docker rm 45034cf698b1` will delete the container with container ID
  `45034cf698b1` if the container is stopped.
* `docker images` will list the docker images that [Docker] has
  downloaded.
* `docker rmi 22cd380ad224` will delete the image with the image ID
  `22cd380ad224` so long as no existing containers depend on the
  image.
* `docker pull jhpyle/docassemble` will download the latest version of
  the **docassemble** image from [Docker Hub] and save it to disk. The
  `docker run` command does this automatically if you tell it to use
  an image that has not been downloaded yet.
* `docker volume ls` will list the [Docker] volumes that exist on the
  system.
* `docker system df` will report how much disk space [Docker] is
  using.

## <a name="upgrading stopping"></a>Stopping the Docker container

The first step of doing a system upgrade is to stop the Docker
container. Use `docker ps` to determine the container ID or name
(e.g., `45034cf698b1`), and then use `docker stop -t 600 45034cf698b1`
to stop the container. The `-t 600` indicates that [Docker] should
wait 600 seconds, or ten minutes, for the container to safely stop.

It is very important that the shutdown is given enough time to
complete, because part of the shutdown process involves dumping the
SQL database, saving the Redis database, and copying files to [data
storage].

Doing `docker stop -t 600` gives the machine ten minutes to shut down,
which is probably more than enough time. If it actually takes 10
minutes for the `docker stop` command to complete, then you should do
`docker ps -a` to see what the exit status was. If it says something
like `Exited (0) About a minute ago`, then that is good, because the
exit status was `0`. If the exit status was something else, that means
Docker had to forcibly kill the container, which may have interrupted
the container's backup process. In that case, you should start the
container again, wait for it to boot, and then do the shutdown again,
but give it even more time to shut down. Or, you may need to
investigate why it took so long to shut down in the first place.

It is important to make sure that the backup procedures that were
carried out when you did `docker stop` did not exhaust the disk space
within the container. If the process of backing up the files exhausts
disk space, then your [data storage] may not contain all of your
application data. If you attempt to do a system upgrade when your
[data storage] does not contain all of your application data, your new
container may only work partially, and you may lose application data.

After the `docker stop` process is completed, you should check the
logs of the container. If `45034cf698b1` is the ID of your container
(obtained from `docker ps -a`), you can run:

{% highlight bash %}
docker logs 45034cf698b1
{% endhighlight %}

The end of the output will look something like this:

{% highlight text %}
2023-08-20 12:17:56,718 INFO stopped: postgres (exit status 0)
2023-08-20 12:17:56,909 INFO stopped: initialize (exit status 0)
2023-08-20 12:17:56,909 INFO reaped unknown pid 1339 (terminated by SIGTERM)
2023-08-20 12:17:57,870 INFO reaped unknown pid 4162 (exit status 0)
2023-08-20 12:17:57,870 INFO reaped unknown pid 4163 (exit status 0)
2023-08-20 12:17:57,870 INFO reaped unknown pid 4213 (terminated by SIGUSR1)
2023-08-20 12:17:58,122 INFO reaped unknown pid 4280 (terminated by SIGUSR1)
2023-08-20 12:17:59,169 INFO stopped: rabbitmq (exit status 0)
2023-08-20 12:17:59,169 INFO reaped unknown pid 4234 (exit status 0)
2023-08-20 12:17:59,169 INFO reaped unknown pid 4287 (terminated by SIGUSR1)
2023-08-20 12:17:59,169 INFO reaped unknown pid 919 (terminated by SIGUSR1)
{% endhighlight %}

The line `stopped: initialize (exit status 0)` indicates that the
shutdown was safe and disk space was not exhausted. If you see any
other report about the way that the `initialize` process was stopped,
something is wrong and it is probably not safe to do a system
upgrade. If you have exhausted disk space, you haven't lost data,
because the data will still be on the stopped container. However, you
need to make sure you don't delete your Docker container, because it
will contain the data that doesn't exist in [data storage].

If you see that something is wrong after stopping the container, you
might want to inspect the file system of the stopped container without
starting it. This allows you to see the logs that were created when
each of the `supervisord` services were shutting down. To inspect the
file system of a stopped container, you can create a Docker image from
the stopped container, and then use `docker run` to create a container
from that image, with a special "entry point" that simply runs a shell
(instead of running **docassemble**).

{% highlight bash %}
docker commit 352b3835eefc deleteme
docker run -ti --rm --entrypoint=/bin/bash deleteme
{% endhighlight %}

While inside the container, you can inspect the contents of various
log files, particularly the log files inside of
`/var/log/supervisor`. This will allow you to see if anything went
wrong during the shutdown process.

Note that any changes that you make will not have any effect on your
stopped container. You are working with a copy of that container.

When you are done exploring the files of the stopped container, you
can run `exit` to exit. Then you will probably want to delete the
image you created:

{% highlight bash %}
docker rmi deleteme
{% endhighlight %}

If your original container is still running, and you want to check the
available disk space, you can use `docker exec` to get into your
container (see the [troubleshooting] section for instructions), and
then you can do:

{% highlight bash %}
df -h
{% endhighlight %}

This will give a report like:

{% highlight text %}
Filesystem      Size  Used Avail Use% Mounted on
overlay          78G   28G   50G  36% /
tmpfs            64M     0   64M   0% /dev
tmpfs           2.0G     0  2.0G   0% /sys/fs/cgroup
shm              64M   24K   64M   1% /dev/shm
/dev/vda1        78G   28G   50G  36% /etc/hosts
tmpfs           2.0G     0  2.0G   0% /proc/acpi
tmpfs           2.0G     0  2.0G   0% /proc/scsi
tmpfs           2.0G     0  2.0G   0% /sys/firmware
{% endhighlight %}

The important line is the one that relates to the filesystem mounted
on `/`. The `Avail` column indicates how much free space is available.

To find out how much space your uploaded and generated files are
using, you can do:

{% highlight bash %}
du -hs /usr/share/docassemble/files
{% endhighlight %}

This will report something like:

{% highlight text %}
4.1G	/usr/share/docassemble/files
{% endhighlight %}

If you are using [S3] or [Azure blob storage], files are not stored in
`/usr/share/docassemble/files`, but are stored in the cloud. However,
it is still important to have ample free disk space even if you are
using [S3] or [Azure blob storage], because **docassemble** needs disk
space to create backup files before saving them to the cloud.

If you need to free up space on the disk, a good place to start is the
`/usr/share/docassemble/backup` folder. The subdirectories for the
rolling backup, which have names like `08-20`, `08-21`, etc. can be
voluminous. You might want to delete all but the most recent
ones. Then you might want to adjust the [`backup days`] Configuration
directive so that the system does not save so many days of backup.

## <a name="upgrading free"></a>Freeing up disk space

The following three lines will stop all containers, remove all
containers, and then remove all of the images that [Docker] created.

{% highlight bash %}
docker stop -t 600 $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images | awk "{print $3}")
{% endhighlight %}

You should understand what they are doing before you run them. The
first command stops all the containers. It uses the output of `docker
ps -a -q` to get a list of the container IDs of all of the containers
on the system, and passes that list to `docker stop`. The second
command deletes all of the containers on the system. The third command
deletes all the images on the server. This last command frees up the
most disk space. It is usually necessary to remove the containers
first (the [`docker rm`] line), as the containers depend on the
images.

Note that if you try to run these commands, you might get an error
like `"docker stop" requires at least 1 argument.` This is harmless;
it happens when the part inside `$()` does not return any output.

If you don't know what you are doing, do not follow the instructions
above and instead get help, or spend time learning how [Docker] works
before you attempt this. Doing `docker rm` permanently deletes your
server, so it's not something you should be doing unless you know for
a fact that your data are backed up in [data storage].

## <a name="upgrading starting"></a>Starting a new container

Once the old images and containers are deleted, you can upgrade to the
new system version of **docassemble** by running the same `docker run`
command that you ran previously. For example, it might be:

{% highlight text %}
docker run --env-file=env.list \
-v dabackup:/usr/share/docassemble/backup \
-d -p 80:80 -p 443:443 --restart always --stop-timeout 600 \
jhpyle/docassemble
{% endhighlight %}

or, if you are using S3 or Azure Blob Storage, you wouldn't use a
`dabackup` volume:

{% highlight bash %}
docker run --env-file=env.list \
-d -p 80:80 -p 443:443 --restart always --stop-timeout 600 \
jhpyle/docassemble
{% endhighlight %}

The `docker run` command will download the latest version of the
`jhpyle/docassemble` image from [Docker Hub]. However, note that if
you have an old version of that image already present on your system,
`docker run` will use that old version instead of downloading the
new image. If you want to download the new image without doing `docker
run`, you can run:

{% highlight bash %}
docker pull jhpyle/docassemble
{% endhighlight %}

Then you can see the image you have downloaded by running `docker
images`.

If your host OS is old, you may want to upgrade your host OS and
Docker itself while the **docassemble** server is stopped. You may
also want to migrate to a new host.

If you want to move your **docassemble** server to a new host, and
you are using a Docker volume for [data storage], then the steps are:

1. On the existing host, [safely shut down](#upgrading stopping)
   the **docassemble** server using `docker stop`.
2. Create a new host and install Docker on it.
3. Transfer the Docker volume to the new host using:
{% highlight text %}
docker run --rm -v dabackup:/from alpine ash -c "cd /from ; tar -cf - . " | ssh -i cert.rsa username@newhost 'docker run --rm -i -v dabackup:/to alpine ash -c "cd /to ; tar -xpvf - " '
{% endhighlight %}
   where `newhost` is the hostname of the new machine, `username` is the
   name of your user account on that machine, `cert.rsa` is the SSH
   certificate file that allows you to SSH to `newhost`. (It needs to
   be saved to the current working directory on the old machine.) This
   `docker run` command is used with `--rm`, which means the container
   will be automatically deleted as soon as it finishes its work
   (which is to copy files). The name `alpine` refers to a small Linux
   distribution that is useful for performing maintenance operations,
   and `ash` refers to a shell command (similar to `bash` and
   `sh`). This command starts a container on the old machine, where
   the `dabackup` volume is mounted on the container at mount point
   `/from`. The container creates a `.tar` file out of the `dabackup`
   and sends the file as a data stream over the network to the new
   computer, using `ssh`. Using `ssh`, it creates a Docker container
   on the new machine, where a new `dabackup` volume is mounted at
   mount point `/to`. This container receives the `.tar` data stream
   over `ssh` and unpacks it to the `/to` directory. Both of the
   containers are deleted when the work completes, but the `dabackup`
   volume on the new computer remains.
4. Start a new container from the latest **docassemble** image using
   `docker run`.

If you are using S3 or Azure Blob Storage, you can just delete the
host machine and start a new machine. Just remember to save the
contents of your `env.list` file, if you were using one.

If you are not using any form of [data storage], but you want to move
your container from one machine to another machine, you can do so
using [Docker] commands. First, use [`docker stop`] to safely shut
down the container. Then use [`docker commit`] to convert the
container into an image. You can run [`docker images`] to verify that
the image exists on the machine. Then you can use [`docker save`] to
convert the image into a `.tar` file. Then you can copy the `.tar`
file from the old machine to the new machine with a network file
copying command like `scp`. On the new machine, you can use [`docker
load`] to convert that `.tar` file into an image. You can run `docker
images` to verify that the image now exists on the new machine). Then
you can invoke `docker run` on this image (using the same environment
variables and command line switches you used when you ran `docker run`
on the old machine.

# <a name="downgrading"></a>Installing an earlier version of **docassemble** when using Docker

When you do `docker run` or `docker pull`, the only image available on
[Docker Hub] is the "latest" image. To install a version based on an
earlier version of **docassemble**, you can make your own image using
[git].

{% highlight bash %}
git clone {{ site.github.repository_url }}
cd docassemble
git checkout v1.4.84
docker build -t yourname/mydocassemble .
cd ..
docker run -d -p 80:80 -p 443:443 --restart always --stop-timeout 600 yourname/mydocassemble
{% endhighlight %}

The [`docker run`] command that you use may have other options; this
is simply an illustration of creating an image called
`yourname/mydocassemble` and then creating a container from it using
[`docker run`].

Starting with version 0.5, the **docassemble** image is split into two
parts. The `jhpyle/docassemble` image uses `jhpyle/docassemble-os` as
a base image. The `jhpyle/docassemble-os` image consists of the
underlying [Ubuntu] operating system with required [Ubuntu] packages
installed. The `jhpyle/docassemble-os` image is updated much less
frequently than the `jhpyle/docassemble` image. If you want to build
your own version of `jhpyle/docassemble-os`, you can do so by running:

{% highlight bash %}
git clone https://github.com/jhpyle/docassemble-os
cd docassemble-os
git checkout v1.0.12
docker build -t jhpyle/docassemble-os .
cd ..
{% endhighlight %}

The [docassemble-os repository] consists of a [Dockerfile] only. Note
that the first line of the [Dockerfile] in the [docassemble
repository] is:

{% highlight text %}
FROM jhpyle/docassemble-os
{% endhighlight %}

Thus, the `jhpyle/docassemble` image incorporates by reference the
`jhpyle/docassemble-os` base image. The [`docker build`] command
above overwrites the `jhpyle/docassemble-os` image that is stored on
your local machine. If you want, you can edit the [Dockerfile] before
building your custom `jhpyle/docassemble` version so that it
references a different base image.

# <a name="monitoring"></a>Monitoring the health of your container

You will want to make sure that you don't run out of hard drive
space. To receive notifications when your hard drive space runs low,
you can use tools provided by your cloud provider.

For example, DigitalOcean allows you to install the "DigitalOcean
Metrics Agent" on the host operating system. This software sends
information to Digital Ocean about memory and disk usage. You can
configure notifications based on thresholds.

If you are using an EC2 instance, you can configure CloudWatch, which
is AWS's system for cloud infrastructure monitoring. How to do this is
beyond the scope of **docassemble**'s documentation, but one way is to
create an IAM Role that has the `AmazonSSMManagedInstanceCore` and
`CloudWatchAgentServerPolicy` attached to it, and then give your EC2
instance this IAM Role. Then, when your EC2 instance has started, go
to the Monitoring tab and click the Configure CloudWatch Agent
button. If you are using a popular AMI, the SSM Agent should be
installed and running. If it says that the CloudWatch agent is not
installed, press the "Install CloudWatch agent" button. Then you can
select which metrics you want to track. Note that AWS may charge you a
fee per metric, so you may not want to select all of them. In
CloudWatch, you can set up an Alarm that will notify you if a metric
exceeds a threshold. The metric for disk usage, if you enabled it, can
be found under "CWAgent" in the subcategory of "InstanceId, device,
fstype, path."  Select the metric of `disk_used_percent` for the Path
`/`.

On AWS, if you want to set up automated monitoring of whether
**docassemble** is responding, you can set up a Canary in
CloudWatch. See the section on [health check endpoints] for some
endpoints that you can use.

[health check endpoints]: {{ site.baseurl }}/docs/admin.html#endpoints
[Redis]: https://redis.io/
[Docker installation instructions for Windows]: https://docs.docker.com/engine/installation/windows/
[Docker installation instructions for OS X]: https://docs.docker.com/engine/installation/mac/
[Docker]: https://www.docker.com/
[Amazon AWS]: https://aws.amazon.com
[automated build]: https://docs.docker.com/docker-hub/builds/
[scalability of docassemble]: {{ site.baseurl }}/docs/scalability.html
[Amazon Linux]: https://aws.amazon.com/amazon-linux-ami/
[EC2]: https://aws.amazon.com/ec2/
[single-server arrangement]: #single server arrangement
[multi-server arrangement]: #multi server arrangement
[EC2 Container Service]: https://aws.amazon.com/ecs/
[S3]: https://aws.amazon.com/s3/
[supervisor]: http://supervisord.org
[hosted on Docker Hub]: https://hub.docker.com/r/jhpyle/docassemble/
[Docker Hub]: https://hub.docker.com/
[scalability]: {{ site.baseurl }}/docs/scalability.html
[Amazon S3]: https://aws.amazon.com/s3/
[using HTTPS]: #https
[`docassemble/Dockerfile`]: {{ site.github.repository_url }}/blob/master/Dockerfile
[`docassemble/Docker/config/config.yml.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/config.yml.dist
[`docassemble/Docker/initialize.sh`]: {{ site.github.repository_url }}/blob/master/Docker/initialize.sh
[`docassemble/Docker/config/docassemble-http.conf.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/docassemble-http.conf.dist
[`docassemble/Docker/config/docassemble-ssl.conf.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/docassemble-ssl.conf.dist
[`docassemble/Docker/config/docassemble-log.conf.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/docassemble-log.conf.dist
[`docassemble/Docker/config/nginx-http.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/nginx-http.dist
[`docassemble/Docker/config/nginx-ssl.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/nginx-ssl.dist
[`docassemble/Docker/config/nginx-log.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/nginx-log.dist
[`docassemble/Docker/ssl/apache.crt.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/apache.crt.orig
[`docassemble/Docker/ssl/apache.key.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/apache.key.orig
[`docassemble/Docker/ssl/apache.ca.pem.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/apache.ca.pem.orig
[`docassemble/Docker/ssl/nginx.crt.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/nginx.crt.orig
[`docassemble/Docker/ssl/nginx.key.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/nginx.key.orig
[`docassemble/Docker/ssl/exim.crt.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/exim.crt.orig
[`docassemble/Docker/ssl/exim.key.orig`]: {{ site.github.repository_url }}/blob/master/Docker/ssl/exim.key.orig
[`docassemble/Docker/docassemble.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.conf
[`docassemble/Docker/docassemble-supervisor.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble-supervisor.conf
[`docassemble/Docker/docassemble-syslog-ng.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble-syslog-ng.conf
[`docassemble/Docker/syslog-ng.conf`]: {{ site.github.repository_url }}/blob/master/Docker/syslog-ng.conf
[`docassemble/Docker/rabbitmq.config`]: {{ site.github.repository_url }}/blob/master/Docker/rabbitmq.config
[`docassemble/Docker/nginx.logrotate`]: {{ site.github.repository_url }}/blob/master/Docker/nginx.logrotate
[`docassemble/Docker/docassemble.logrotate`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble.logrotate
[`docassemble/Docker/apache.logrotate`]: {{ site.github.repository_url }}/blob/master/Docker/apache.logrotate
[`docassemble/Docker/process-email.sh`]: {{ site.github.repository_url }}/blob/master/Docker/process-email.sh
[`docassemble/Docker/run-postgresql.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-postgresql.sh
[`docassemble/Docker/run-nginx.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-nginx.sh
[`docassemble/Docker/run-uwsgi.sh`]: {{ site.github.repository_url }}/blob/master/Docker/run-uwsgi.sh
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
[PostgreSQL]: https://www.postgresql.org/
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
[`db`]: {{ site.baseurl }}/docs/config.html#db
[`db` section]: {{ site.baseurl }}/docs/config.html#db
[`s3` section]: {{ site.baseurl }}/docs/config.html#s3
[`azure` section]: {{ site.baseurl }}/docs/config.html#azure
[Build your own private image]: #build
[Redis]: https://redis.io/
[RabbitMQ]: https://www.rabbitmq.com/
[Application Load Balancer]: https://aws.amazon.com/elasticloadbalancing/applicationloadbalancer/
[IAM]: https://aws.amazon.com/iam/
[Amazon]: https://amazon.com
[load balancer]: https://en.wikipedia.org/wiki/Load_balancing_(computing)
[S3 Console]: https://console.aws.amazon.com/s3/home
[IAM Console]: https://console.aws.amazon.com/iam
[create your own Docker image]: #build
[`certs`]: {{ site.baseurl }}/docs/config.html#certs
[cron]: https://en.wikipedia.org/wiki/Cron
[Python virtual environment]: https://docs.python-guide.org/dev/virtualenvs/
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
[`S3REGION`]: #S3REGION
[`S3SECRETACCESSKEY`]: #S3SECRETACCESSKEY
[`AZURECONTAINER`]: #AZURECONTAINER
[`AZUREACCOUNTNAME`]: #AZUREACCOUNTNAME
[`AZUREACCOUNTKEY`]: #AZUREACCOUNTKEY
[`CONTAINERROLE`]: #CONTAINERROLE
[`SERVERHOSTNAME`]: #SERVERHOSTNAME
[`DAHOSTNAME`]: #DAHOSTNAME
[`USEHTTPS`]: #USEHTTPS
[`USELETSENCRYPT`]: #USELETSENCRYPT
[`DAEXPOSEWEBSOCKETS`]: #DAEXPOSEWEBSOCKETS
[`DAWEBSOCKETSIP`]: #DAWEBSOCKETSIP
[`DAWEBSOCKETSPORT`]: #DAWEBSOCKETSPORT
[`DAUPDATEONSTART`]: #DAUPDATEONSTART
[Celery]: https://docs.celeryq.dev/en/stable/
[background task]: {{ site.baseurl }}/docs/background.html#background
[background process]: {{ site.baseurl }}/docs/background.html#background
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
[`kubernetes`]: {{ site.baseurl }}/docs/config.html#kubernetes
[`ubuntu packages`]: {{ site.baseurl }}/docs/config.html#ubuntu packages
[`url root`]: {{ site.baseurl }}/docs/config.html#url root
[`root`]: {{ site.baseurl }}/docs/config.html#root
[Ubuntu]: https://ubuntu.com/
[Debian]: https://www.debian.org/
[using S3]: #persistent s3
[using Azure blob storage]: #persistent azure
[environment variables]: #configuration options
[GitHub]: https://github.com
[data storage]: #data storage
[`docker stop`]: https://docs.docker.com/engine/reference/commandline/stop/
[`docker kill`]: https://docs.docker.com/engine/reference/commandline/kill/
[`docker rm`]: https://docs.docker.com/engine/reference/commandline/rm/
[`docker rmi`]: https://docs.docker.com/engine/reference/commandline/rmi/
[`docker exec`]: https://docs.docker.com/engine/reference/commandline/exec/
[`docker start`]: https://docs.docker.com/engine/reference/commandline/start/
[`docker run`]: https://docs.docker.com/engine/reference/commandline/run/
[`docker build`]: https://docs.docker.com/engine/reference/commandline/build/
[`docker ps`]: https://docs.docker.com/engine/reference/commandline/ps/
[`docker images`]: https://docs.docker.com/engine/reference/commandline/images/
[`docker pull`]: https://docs.docker.com/engine/reference/commandline/pull/
[`docker volume`]: https://docs.docker.com/engine/reference/commandline/volume/
[`docker volume inspect`]: https://docs.docker.com/engine/reference/commandline/volume_inspect/
[`docker volume create`]: https://docs.docker.com/engine/reference/commandline/volume_create/
[`docker commit`]: https://docs.docker.com/engine/reference/commandline/commit/
[`docker save`]: https://docs.docker.com/engine/reference/commandline/save/
[`docker load`]: https://docs.docker.com/engine/reference/commandline/load/
[Amazon Web Services]: https://aws.amazon.com
[AWS]: https://aws.amazon.com
[S3 bucket]: https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
[scheduled tasks]: {{ site.baseurl }}/docs/background.html#scheduled
[WebSocket]: https://en.wikipedia.org/wiki/WebSocket
[e-mails]: {{ site.baseurl }}/docs/background.html#email
[e-mail receiving]: {{ site.baseurl }}/docs/background.html#email
[Exim]: https://en.wikipedia.org/wiki/Exim
[TLS]: https://en.wikipedia.org/wiki/Transport_Layer_Security
[`incoming mail domain`]: {{ site.baseurl }}/docs/config.html#incoming mail domain
[git]: https://en.wikipedia.org/wiki/Git
[without Let's Encrypt]: #own certificates
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
[Security Group]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html
[HTTP]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
[region]: https://docs.aws.amazon.com/general/latest/gr/rande.html
[`secretkey`]: {{ site.baseurl }}/docs/config.html#secretkey
[Cross-Origin Resource Sharing]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[`cross site domains`]: {{ site.baseurl }}/docs/config.html#cross site domains
[`server administrator email`]: {{ site.baseurl }}/docs/config.html#server administrator email
[e-mail setup]: {{ site.baseurl }}/docs/installation.html#setup_email
[installation]: {{ site.baseurl }}/docs/installation.html
[e-mailing the interview]: {{ site.baseurl }}/docs/background.html#email
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[virtual machine]: https://en.wikipedia.org/wiki/Virtual_machine
[upgrading]: #upgrading
[`Dockerfile`]: {{ site.github.repository_url }}/blob/master/Dockerfile
[Logs]: {{ site.baseurl }}/docs/admin.html#logs
[Supervisor]: http://supervisord.org
[syslog-ng]: https://en.wikipedia.org/wiki/Syslog-ng
[database corruption]: #shutdown
[debugging subsection]: {{ site.baseurl }}/docs/installation.html#debug
[Traefik]: https://traefik.io/
[Flask]: https://flask.pocoo.org/
[third party providers]: {{ site.baseurl }}/deploy.html
[example deployment]: {{ site.baseurl }}/deploy.html#example
[troubleshooting]: #troubleshooting
[`backup days`]: {{ site.baseurl }}/docs/config.html#backup days
[`python packages`]: {{ site.baseurl }}/docs/config.html#python packages
[`xsendfile`]: {{ site.baseurl }}/docs/config.html#xsendfile
[`ls`]: https://kb.iu.edu/d/afsk#ls
[`cd`]: https://kb.iu.edu/d/afsk#cd
[`less`]: https://kb.iu.edu/d/afsk#less
[`nano`]: https://wiki.gentoo.org/wiki/Nano/Basics_Guide
[`vi`]: https://www.engadget.com/2012/07/10/vim-how-to/
[WSGI]: https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[pip]: https://en.wikipedia.org/wiki/Pip_%28package_manager%29
[Configuration]: {{ site.baseurl }}/docs/config.html
[`expose websockets`]: {{ site.baseurl }}/docs/config.html#expose websockets
[`websockets ip`]: {{ site.baseurl }}/docs/config.html#websockets ip
[`websockets port`]: {{ site.baseurl }}/docs/config.html#websockets port
[Logs]: {{ site.baseurl }}/docs/admin.html#logs
[web interface]: {{ site.baseurl }}/docs/admin.html#configuration
[behind a reverse proxy]: #forwarding
[live help]: {{ site.baseurl }}/docs/livehelp.html
[`DARedis`]: {{ site.baseurl }}/docs/objects.html#DARedis
[NGINX]: https://www.nginx.com/
[uWSGI]: https://uwsgi-docs.readthedocs.io/en/latest/
[docassemble-os repository]: https://github.com/jhpyle/docassemble-os
[Dockerfile]: https://docs.docker.com/engine/reference/builder/
[`web server`]: {{ site.baseurl }}/docs/config.html#web server
[`docker stop -t 600`]: https://docs.docker.com/engine/reference/commandline/stop/
[MinIO]: https://min.io/
[`use minio`]: {{ site.baseurl }}/docs/config.html#use minio
[Kubernetes]: https://kubernetes.io/
[`collect statistics`]: {{ site.baseurl }}/docs/config.html#collect statistics
[Kubernetes]: https://kubernetes.io/
[`update on start`]: {{ site.baseurl }}/docs/config.html#update on start
[`allow updates`]: {{ site.baseurl }}/docs/config.html#allow updates
[`stable version`]: {{ site.baseurl }}/docs/config.html#stable version
[`ssl_protocols`]: https://nginx.org/en/docs/http/configuring_https_servers.html
[`ssl_ciphers`]: https://nginx.org/en/docs/http/configuring_https_servers.html
[`sql ping`]: {{ site.baseurl }}/docs/config.html#sql ping
[with Kubernetes]: https://github.com/jhpyle/charts
[Rook]: https://rook.io/docs/rook/v0.8/object.html
[Vultr]: https://www.vultr.com/docs/vultr-object-storage
[Google Cloud]: https://cloud.google.com/storage/docs/interoperability
[Wasabi]: https://wasabi.com/s3-compatible-cloud-storage/
[Linode]: https://www.linode.com/docs/platform/object-storage/how-to-use-object-storage/
[Digital Ocean]: https://developers.digitalocean.com/documentation/spaces/#aws-s3-compatibility
[IBM Cloud]: https://cloud.ibm.com/apidocs/cos/cos-compatibility
[Oracle Cloud]: https://docs.cloud.oracle.com/en-us/iaas/Content/Object/Tasks/s3compatibleapi.htm
[Scaleway]: https://www.scaleway.com/en/object-storage/
[Exoscale]: https://www.exoscale.com/object-storage/
[`S3ENDPOINTURL`]: #S3ENDPOINTURL
[`use cloud urls`]: {{ site.baseurl }}/docs/config.html#use cloud urls
[YAML]: https://en.wikipedia.org/wiki/YAML
[`nginx ssl protocols`]: {{ site.baseurl }}/docs/config.html#nginx ssl protocols
[`nginx ssl ciphers`]: {{ site.baseurl }}/docs/config.html#nginx ssl ciphers
[Helm]: https://helm.sh/
[`BEHINDHTTPSLOADBALANCER`]: #BEHINDHTTPSLOADBALANCER
[BusyBox]: https://hub.docker.com/_/busybox
[`http port`]: {{ site.baseurl }}/docs/config.html#http port
[`celery processes`]: {{ site.baseurl }}/docs/config.html#celery processes
[bash]: https://en.wikipedia.org/wiki/Bash_(Unix_shell)
[`backup file storage`]: {{ site.baseurl }}/docs/config.html#backup file storage
[Docker volume]: https://docs.docker.com/storage/volumes/
[Docker volumes]: https://docs.docker.com/storage/volumes/
[`pip index url`]: {{ site.baseurl }}/docs/config.html#pip index url
[`pip extra index urls`]: {{ site.baseurl }}/docs/config.html#pip extra index urls
[ARM]: https://en.wikipedia.org/wiki/ARM_architecture_family
[`debug`]: {{ site.baseurl }}/docs/config.html#debug
[`allow demo`]: {{ site.baseurl }}/docs/config.html#allow demo
[`enable playground`]: {{ site.baseurl }}/docs/config.html#enable playground
[`allow configuration editing`]: {{ site.baseurl }}/docs/config.html#allow configuration editing
[`supervisor`]: {{ site.baseurl }}/docs/config.html#supervisor
[Docker Desktop]: https://docs.docker.com/desktop/install/mac-install/
[Pandoc]: https://pandoc.org
[LibreOffice]: https://www.libreoffice.org/
[containerd]: https://containerd.io/
[runC]: https://github.com/opencontainers/runc
[Live Help]: {{ site.baseurl }}/docs/livehelp.html
[DNS]: https://en.wikipedia.org/wiki/Domain_Name_System
[`<iframe>`]: https://www.w3schools.com/tags/tag_iframe.asp
[embed]: {{ site.baseurl }}/docs/interviews.html#iframe
[Cross-Origin Resource Sharing]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[CORS]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[`certbot`]: https://certbot.eff.org/
[SSH client]: https://www.ssh.com/academy/ssh/client
[Apache]: https://httpd.apache.org/
[tz database]: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
[locale values]: {{ site.baseurl }}/img/locales.txt
[`enable unoconv`]: {{ site.baseurl }}/docs/config.html#enable unoconv
[`gotenberg url`]: {{ site.baseurl }}/docs/config.html#gotenberg url
[`use nginx to serve files`]: {{ site.baseurl }}/docs/config.html#use nginx to serve files
[Gotenberg]: https://gotenberg.dev/
[deletes inactive sessions]: {{ site.baseurl }}/docs/config.html#interview delete days
[receiving emails]: {{ site.baseurl }}/docs/functions.html#interview_email
[unoconv]: https://linux.die.net/man/1/unoconv
[AWS CLI]: https://aws.amazon.com/cli/
[Azure CLI]: https://learn.microsoft.com/en-us/cli/azure/
[Amazon Lightsail]: https://aws.amazon.com/lightsail/
[`locale`]: {{ site.baseurl }}/docs/config.html#locale
[Alembic]: https://alembic.sqlalchemy.org/en/latest/
[docassemble repository]: {{ site.github.repository_url }}
