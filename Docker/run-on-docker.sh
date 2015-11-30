#! /bin/sh
/etc/init.d/postgresql start
/etc/init.d/apache2 start
/usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
/etc/init.d/apache2 stop
/etc/init.d/postgresql stop
