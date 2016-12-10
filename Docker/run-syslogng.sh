#! /bin/bash

export DA_ACTIVATE="${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"

source /dev/stdin < <(su -c "source $DA_ACTIVATE && python -m docassemble.base.read_config" www-data)

exec /usr/sbin/syslog-ng --foreground --no-caps
