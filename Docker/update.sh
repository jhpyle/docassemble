#! /bin/bash

source "${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"
export CONTAINERROLE=":${CONTAINERROLE:-all}:"
export HOME=/var/www

python -m docassemble.webapp.update

exit 0
