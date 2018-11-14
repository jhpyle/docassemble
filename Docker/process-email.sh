#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
source "${DA_PYTHON:-${DA_ROOT}/local}/bin/activate"

emailfile=$(mktemp)

cat >$emailfile
python -m docassemble.webapp.process_email $emailfile
rm -f $emailfile
