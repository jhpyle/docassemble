#! /bin/bash

if [ "${WWWUID:-none}" == "none" ] || [ "${WWWGID:-none}" == "none" ]; then
    exit 0
fi

OLDUID=`id -u www-data`
OLDGID=`id -g www-data`

usermod -o -u $WWWUID www-data
groupmod -g $WWWGID www-data
find / -user $OLDUID -exec chown -h www-data {} \;
find / -group $OLDGID -exec chgrp -h www-data {} \;
    
