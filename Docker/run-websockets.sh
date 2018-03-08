#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
source "${DA_PYTHON:-${DA_ROOT}/local}/bin/activate"
export HOME=/var/www

exec python -m docassemble.webapp.socketserver
