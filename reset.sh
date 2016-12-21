#! /bin/bash

supervisorctl stop apache2
su -c "dropdb docassemble" postgres
su -c "createdb -O www-data docassemble" postgres
su -c "/usr/share/docassemble/local/bin/python -m docassemble.webapp.create_tables" www-data
rm -rf /usr/share/docassemble/files/0*
supervisorctl start apache2

