#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
export DAPYTHONVERSION="${DAPYTHONVERSION:-3}"
export DA_DEFAULT_LOCAL="local3.8"

export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source "${DA_ACTIVATE}"

emailfile="$(mktemp)"

cat > "$emailfile"
python -m docassemble.webapp.process_email "$emailfile"
rm -f "$emailfile"
