#! /bin/bash

dirs="admin daglobal files mail objectstore sms users api develop interview main packages translation auth emailserver jsonstorage ml phonelogin tts core fax logs monitor react twilio"

for dir in $dirs; do
    if [ "$dir" = "blueprints" ]; then
	continue
    fi
    name=$(basename "$dir")
    if [ ! -f "$dir/__init__.py" ]; then
	read -r -d '' contents <<EOF
from flask import Blueprint

${name}_bp = Blueprint(
    '$name',
    __name__
)

from . import views

EOF
	echo -e "$contents" > "$dir/__init__.py"
    fi
    if [ -f "$dir/views.py" ]; then
	sed -i 's/^@app\./@'${name}'_bp./' "$dir/views.py"
    fi
done
