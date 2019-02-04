#!/bin/bash

export DA_ROOT="${DA_ROOT:-/usr/share/docassemble}"
if [ "${DAPYTHONVERSION}" == "2" ]; then
    export DA_DEFAULT_LOCAL="local"
else
    export DA_DEFAULT_LOCAL="local3.5"
fi
export DA_ACTIVATE="${DA_PYTHON:-${DA_ROOT}/${DA_DEFAULT_LOCAL}}/bin/activate"
source ${DA_ACTIVATE}

emailfile=$(mktemp)

cat > $emailfile
python -m docassemble.webapp.process_email $emailfile
rm -f $emailfile
