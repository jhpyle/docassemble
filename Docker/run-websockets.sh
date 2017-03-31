#!/bin/bash

export DA_ACTIVATE="${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"
source $DA_ACTIVATE
export HOME=/var/www

exec python -m docassemble.webapp.socketserver
