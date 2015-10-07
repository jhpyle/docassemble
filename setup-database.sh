#! /bin/sh

/etc/init.d/postgresql start
echo 'create role "www-data" login; create database docassemble;' | su -c psql postgres 
su -c "python docassemble_webapp/docassemble/webapp/create_tables.py" postgres
echo 'grant all on all tables in schema public to "www-data"; grant all on all sequences in schema public to "www-data";' | su -c "psql docassemble" postgres
/etc/init.d/postgresql stop


