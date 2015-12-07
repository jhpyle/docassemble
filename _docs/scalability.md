---
layout: docs
title: Scalability of docassemble
short_title: Scalability
---

**docassemble** is easily scalable.  It does not store any user
information in memory or in an in-memory cache.  Rather, it uses a SQL
database to store user answers and a filesystem to store user
documents.  As a result, a cluster of servers can serve responses to
client browsers if each cluster member is configured to point to the
same SQL database and mount the same filesystem.

Each server's [configuration] is defined in `/etc/docassemble/config.yml`.
The default configuration for the SQL connection is:

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
This configuration can be modified to connect to use password
authentication on a remote server.

The location of uploaded user files is defined in this line of
`config.yml`:

{% highlight yaml %}
uploads: /usr/share/docassemble/files
{% endhighlight %}

When developers install new Python packages, the packages are unpacked
in `/usr/share/docassemble/local`, and the web server is restarted by
"touch"ing the WSGI file,
`/usr/share/docassemble/webapp/docassemble.wsgi`.  The path of the
WSGI file is defined in the [Apache configuration] and in the
**docassemble** configuration file:

{% highlight yaml %}
webapp: /var/lib/docassemble/docassemble.wsgi
{% endhighlight %}

Configuring a cluster of **docassemble** servers entails creating a
central network file server to store uploaded files, which the
application servers would use.  The easiest way to do this is with
[Amazon S3], for which **docassemble** has built-in integration; you
can set this up in the [configuration].  In addition, the `db` section
of the `config.yml` file on each server must be written to point to a
central SQL server.

[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[Apache configuration]: {{ site.baseurl }}/docs/installation.html
[configuration]: {{ site.baseurl }}/docs/config.html
[installation]: {{ site.baseurl }}/docs/installation.html
