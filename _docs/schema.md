---
layout: docs
title: SQL database schema
short_title: SQL Schema
---

The **docassemble** web application requires a central SQL server.
The [`db`] directive in the [configuration] tells **docassemble**
where to find this SQL database.

The necessary data tables are created with the
[`docassemble.webapp.create_tables`] module.  If new versions of
**docassemble** add new tables or modify the columns of existing
tables, the [`docassemble.webapp.create_tables`] module uses [alembic]
to make these changes to the database.

The [`docassemble.webapp.create_tables`] module runs automatically
within the [Docker] container whenever the container [starts up] or
when the server [restarts] (e.g., when a package is installed or
upgraded).

The following table lists all of the tables and columns that
**docassemble** uses.  (This is output from [PostgreSQL], but the same
concepts exist in most SQL database systems.)

{% include db-schema.html %}

[starts up]: {{ site.github.repository_url }}/blob/master/Docker/initialize.sh
[restarts]: {{ site.github.repository_url }}/blob/master/Docker/reset.sh
[alembic]: http://alembic.zzzcomputing.com/en/latest/
[PostgreSQL]: https://www.postgresql.org/
[SQLAlchemy]: http://www.sqlalchemy.org/
[Docker]: {{ site.baseurl }}/docs/docker.html
[configuration]: {{ site.baseurl }}/docs/config.html
[installation]: {{ site.baseurl }}/docs/installation.html
[`db`]: {{ site.baseurl }}/docs/config.html#db
[`schema file`]: {{ site.baseurl }}/docs/config.html#db schema file
[`docassemble.webapp.create_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/create_tables.py
[`docassemble.webapp.fix_postgresql_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/fix_postgresql_tables.py
[`db-schema.txt`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/data/db-schema.txt
