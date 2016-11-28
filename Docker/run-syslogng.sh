#! /bin/bash

export DA_CONFIG_FILE=/usr/share/docassemble/config/config.yml

source /dev/stdin < <(su -c "source /usr/share/docassemble/local/bin/activate && python -m docassemble.base.read_config $DA_CONFIG_FILE" www-data)

/usr/sbin/syslog-ng --foreground --no-caps
