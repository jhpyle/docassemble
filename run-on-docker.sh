#! /bin/sh

/etc/init.d/postgresql start
/usr/sbin/apache2 -D FOREGROUND
