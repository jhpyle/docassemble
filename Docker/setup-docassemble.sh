#! /bin/sh

/etc/init.d/postgresql start || exit 1
echo "drop database if exists docassemble; drop role if exists docassemble; create role docassemble with login password 'abc123'; create database docassemble owner docassemble;" | su -c psql postgres || exit 1
su -c "source /usr/share/docassemble/local/bin/activate && python -m docassemble.webapp.create_tables /usr/share/docassemble/config.yml" postgres || exit 1
/etc/init.d/postgresql stop || exit 1
