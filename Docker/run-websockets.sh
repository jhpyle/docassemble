#!/bin/bash

export DA_ACTIVATE="${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"
source $DA_ACTIVATE

exec python -m docassemble.webapp.socketserver
