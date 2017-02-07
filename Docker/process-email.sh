#!/bin/bash

emailfile=$(mktemp)

source "${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"

cat > $emailfile
python -m docassemble.webapp.process_email $emailfile
rm -f $emailfile
