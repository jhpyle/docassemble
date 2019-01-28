#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DA_PYTHON_VERSION="${DA_PYTHON_VERSION:-2}"
if [ "${DA_PYTHON_VERSION}" == "2" ]; then
    export DA_DEFAULT_LOCAL="local"
else
    export DA_DEFAULT_LOCAL="local3.5"
fi
export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source $DA_ACTIVATE
export HOME=/var/www

exec python -m docassemble.webapp.socketserver
