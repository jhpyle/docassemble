#! /bin/bash

source /etc/profile
source /usr/share/docassemble/local/bin/activate
pip install --upgrade -r requirements.txt && touch /usr/share/docassemble/webapp/docassemble.wsgi
history -s "source /usr/share/docassemble/local/bin/activate"
history -s "pip install --upgrade -r requirements.txt && touch /usr/share/docassemble/webapp/docassemble.wsgi"
