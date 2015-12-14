---
layout: docs
title: Scalability of docassemble
short_title: Scalability
---

**docassemble** is easily scalable.  It does not store any user
information in memory or in an in-memory cache.  Rather, it uses a SQL
database (accessed through [SQLAlchemy]) to store user answers and a
file store (filesystem or [Amazon S3]) to store user documents.  As a
result, a cluster of servers can serve responses to client browsers if
each cluster member is configured to point to the same SQL database
and use the same file store.

# Quick start

If you want to run **docassemble** in a multi-server arrangement,
there are a variety of ways to do so, but the following is the
recommended method:

1. Get an [Amazon Web Services] account.
2. Go to [Amazon S3] and obtain an access key and a secret access
key.  Create a bucket.
3. Go to [Amazon EC2] and launch two [Amazon Linux] instances in the
same [Virtual Private Cloud] (VPC).
4. Edit your VPC so that "DNS Resolution" Yes and "DNS Hostnames" is
   Yes.
5. Install [Docker] in both instances: `sudo yum -y update && sudo yum
-y install docker && sudo usermod -a -G docker ec2-user`.  Then log
out and log back in again.  See [Amazon's Docker instructions] for
more information.
6. In the first [EC2] instance, start a PostgreSQL container using the
official **docassemble** [Docker] image: `docker run -d -p 5432:5432
jhpyle/docassemble-sql`.
7. Note the "Private DNS" hostname of this instance.  Then go to
[Amazon Route 53] and create a Hosted Zone with the type "Private
Hosted Zone for Amazon VPC."  Use a domain like `docassemble.local` or
whatever you want (this is purely internal).  Create a CNAME that maps
`sql.docassemble.local` (or other name of your choosing) to the
"Private DNS" hostname of the instance running the SQL server.  This
is so that the application servers can locate the SQL server by
`sql.docassemble.local`.  Alternatively, you could forget about
[Amazon Route 53] and just use the "Private IP" address of the SQL
instance in place of the hostname, but it is nicer to be able to use
DNS, in case the underlying IP address ever changes.
8. Go to the other [EC2] instance and create a file called `env.list`:
{% highlight text %}
CONTAINERROLE=webserver
DBNAME=docassemble
DBUSER=docassemble
DBPASSWORD=abc123
DBHOST=sql.docassemble.local
S3ENABLE=true
S3ACCESSKEY=FWIEJFIJIDGISEJFWOEF
S3SECRETACCESSKEY=RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
S3BUCKET=yourbucketname
{% endhighlight %}
Substitute your own values for `DBHOST`, `S3ACCESSKEY`,
`S3SECRETACCESSKEY`, and `S3BUCKET`.
9. Run `docker run --env-file=env.list -d -p 80:80 -p 443:443
jhpyle/docassemble`
10. Edit the [security group] on the second instance to allow HTTP
traffic from anywhere.
11. Point your browser to the "Public IP" of the second instance.  A
**docassemble** interview should appear.
12. You can create as many additional instances as you want and deploy
**docassemble** on them by repeating steps 8-9.  Make sure these new
instances use the same security group, so you don't have to repeat
step 10.
13. Add the instances (other than the SQL instance) to a load balancer

# Explanation

Each server's [configuration] is defined in
`/usr/share/docassemble/config.yml`.  The default configuration for
the SQL connection is:

{% highlight yaml %}
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: null
  password: null
  host: null
  port: null
{% endhighlight %}

This will cause **docassemble** to connect to PostgreSQL on the local
machine with peer authentication and use the database "docassemble."
This configuration can be modified to connect to a remote server.

Configuring a cluster of **docassemble** servers requires centralizing
the location of uploaded files, either by using an [Amazon S3] bucket
(the `s3` [configuration] setting) or by making the uploaded file
directory a network drive mount (the `uploads` [configuration]
setting).

The default location of uploaded user files is defined by the
`uploads` [configuration] setting:

{% highlight yaml %}
uploads: /usr/share/docassemble/files
{% endhighlight %}

However, **docassemble** will use [Amazon S3] instead of this folder
if access keys are provided as follows:

{% highlight yaml %}
s3:
  enable: true
  access_key_id: FWIEJFIJIDGISEJFWOEF
  secret_access_key: RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
  bucket: yourbucketname
{% endhighlight %}

When developers install new Python packages, the packages are unpacked
in `/usr/share/docassemble/local` (controlled by [configuration]
variable `packages`).

The web server will restart, and re-read its Python source code, if
the modification time on the WSGI file,
`/usr/share/docassemble/webapp/docassemble.wsgi`, is changed.  The
path of the WSGI file is defined in the [Apache configuration] and in
the **docassemble** configuration file:

{% highlight yaml %}
webapp: /usr/share/docassemble/docassemble.wsgi
{% endhighlight %}

# Synchronizing configuration and installs with supervisor

If you are using Amazon EC2, set the following in the [configuration]:

{% highlight yaml %}
ec2: true
{% endhighlight yaml %}

# SQL server

To start a postgresql server in an [Amazon Linux] instance:

{% highlight bash %}
sudo yum install postgresql-server
sudo service postgresql initdb
sudo service postgresql start
sudo -u postgres createuser --login --pwprompt docassemble
sudo -u postgres createdb --owner=docassemble docassemble
{% endhighlight %}

The "createuser" line will ask for a password; enter something like `abc123`.

Now that the server is running, you can set up web servers to
communicate with the server by setting something like the following in
the [configuration]:

{% highlight yaml %}
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: docassemble
  password: abc123
  host: 192.168.0.56
  port: null
  table_prefix: null
{% endhighlight %}

If you installed the web servers before installing the SQL server,
note that the `create_tables` module will need to be run in order to
create the database tables that **docassemble** expects.

# Mail server

If you are launching **docassemble** within [EC2], note that Amazon does
not allow e-mail to be sent from SMTP servers operating within an [EC2]
instance, unless you obtain special permission.  Therefore, you may
wish to use an SMTP server on the internet with which you can connect
through [SMTP Authentication]. 

If you have a Google account, you can use Google's SMTP server by
setting the following in your [configuration]:

{% highlight yaml %}
mail:
  server: smtp.gmail.com
  username: yourgoogleusername
  password: yourgooglepassword
  use_ssl: true
  port: 465
  default_sender: '"Administrator" <no-reply@example.com>'
{% endhighlight %}

Note that for this to work, you will need to go into your Google
settings and set "Allow less secure apps" to "ON."

Alternatively, you could set up an e-mail server on [Amazon SES].  It
is easy to set up, but in order to get permission to send e-mails to
the outside world, you will need to explain to Amazon what your
purposes for sending e-mail are, and explain your policy of dealing
with replies and bounce-backs.

# Using SSL certificates

If you want to use HTTPS, you will need SSL certificates.  The default
Apache configuration file expects these certificates to be located in
the following files:

{% highlight text %}
SSLCertificateFile /etc/ssl/docassemble/docassemble.crt
SSLCertificateKeyFile /etc/ssl/docassemble/docassemble.key 
SSLCertificateChainFile /etc/ssl/docassemble/docassemble.ca.pem
{% endhighlight %}

In order to make sure that these files are replicated on every web
server, the [supervisor] will run the
`docassemble.webapp.install_certs` module before running the web
server.

If you are using S3, this module will copy the files from the `certs/`
prefix in your bucket to `/etc/ssl/docassemble`.

If you are not using S3, this module will copy the files from
`/usr/share/docassemble/certs` to `/etc/ssl/docassemble`.

The files need to be called `docassemble.crt`, `docassemble.key`, and
`docassemble.ca.pem`, or whatever the web server configuration
expects.

First, obtain your SSL certificates.  Name them `docassemble.crt`, `docassemble.key`, and
`docassemble.ca.pem`.

If you have enabled `s3` in the [configuration], copy the certificate
files to the `certs/` prefix of the `bucket` you configured:

{% highlight bash %}
s3cmd --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY put yourserver.crt s3://yourbucket/certs/docassemble.crt
s3cmd --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY put yourserver.key s3://yourbucket/certs/docassemble.key
s3cmd --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY put yourserver.ca.pem s3://yourbucket/certs/docassemble.ca.pem
{% endhighlight %}

If you do not have the s3cmd utility, install it:

{% highlight bash %}
apt-get install s3cmd
{% endhighlight %}

If you did not enable `s3`, just copy `docassemble.crt`, `docassemble.key`, and
`docassemble.ca.pem` to `/usr/share/docassemble/certs` on each web
server instance.

If you need to use different filesystem or S3 locations, you can edit
the [configuration] variables `certs` and `cert_install_directory`.

[SMTP Authentication]: https://en.wikipedia.org/wiki/SMTP_Authentication
[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[Apache configuration]: {{ site.baseurl }}/docs/installation.html
[configuration]: {{ site.baseurl }}/docs/config.html
[installation]: {{ site.baseurl }}/docs/installation.html
[SQLAlchemy]: http://www.sqlalchemy.org/
[Amazon S3]: https://aws.amazon.com/s3/
[Amazon EC2]: https://aws.amazon.com/ec2/
[EC2]: https://aws.amazon.com/ec2/
[Amazon SES]: https://aws.amazon.com/ses/
[Amazon Linux]: https://aws.amazon.com/amazon-linux-ami/
[Amazon Web Services]: https://aws.amazon.com
[Docker]: https://www.docker.com/
[Amazon's Docker instructions]:
http://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html
[Virtual Private Cloud]: https://aws.amazon.com/vpc/
[Amazon Route 53]: https://aws.amazon.com/route53/
[security group]: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html
