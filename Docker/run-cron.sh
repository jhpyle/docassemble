#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-2}"
if [ "${DAPYTHONVERSION}" == "2" ]; then
    export DA_DEFAULT_LOCAL="local"
else
    export DA_DEFAULT_LOCAL="local3.5"
fi
export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
export HOME=/var/www
export CRONTYPE=${1:-cron_daily}

exec su -c "source $DA_ACTIVATE && python -m docassemble.webapp.cron -type $CRONTYPE" www-data
