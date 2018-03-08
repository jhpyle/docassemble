#! /bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
source "${DA_PYTHON:-${DA_ROOT}/local}/bin/activate"
export CONTAINERROLE=":${CONTAINERROLE:-all}:"
export HOME=/var/www

python -m docassemble.webapp.update

exit 0
