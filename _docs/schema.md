---
layout: docs
title: SQL database schema
short_title: SQL schema
---

The **docassemble** web application requires a central SQL server.
The [`db`] directive in the [configuration] tells **docassemble**
where to find this SQL database.

The necessary data tables are created with the
[`docassemble.webapp.create_tables`] module:

{% highlight bash %}
python -m docassemble.webapp.create_tables
{% endhighlight %}

Thus, if new versions of **docassemble** add new database tables, this
module will create the tables.  But if new versions of **docassemble**
add columns to existing tables, the
[`docassemble.webapp.create_tables`] module (which is based on
[SQLAlchemy]) will not be able to add those additional columns.

If you are using [PostgreSQL] as your backend database, the
[`docassemble.webapp.fix_postgresql_tables`] module will add these
missing columns:

{% highlight bash %}
python -m docassemble.webapp.fix_postgresql_tables
{% endhighlight %}

This module depends on a file called [`db-schema.txt`], which is
stored in `/usr/share/docassemble/config/`.  This file will exist if
you are using [Docker] or if you followed the [installation]
instructions and copied necessary files into this folder.  (The
location of this file is configurable with the [`schema_file`]
directive under [`db`] in the [configuration].)

If you are running **docassemble** with [Docker], these two database
update modules will execute automatically during the container
startup, and you shouldn't have to worry about upgrading your database
tables.

If you are using a SQL database other than [PostgreSQL], however, you
might need to make manual changes to existing database tables after a
**docassemble** upgrade.

The following table lists all of the tables and columns that
**docassemble** uses.  (This is output from [PostgreSQL], but the same
concepts exist in most SQL database systems.)

{% include db-schema.html %}

[PostgreSQL]: https://www.postgresql.org/
[SQLAlchemy]: http://www.sqlalchemy.org/
[Docker]: {{ site.baseurl }}/docs/docker.html
[configuration]: {{ site.baseurl }}/docs/config.html
[installation]: {{ site.baseurl }}/docs/installation.html
[`db`]: {{ site.baseurl }}/docs/config.html#db
[`schema_file`]: {{ site.baseurl }}/docs/config.html#schema_file
[`docassemble.webapp.create_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/create_tables.py
[`docassemble.webapp.fix_postgresql_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/fix_postgresql_tables.py
[`db-schema.txt`]: {{ site.github.repository_url }}/blob/master/Docker/db-schema.txt
