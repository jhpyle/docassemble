#!/bin/bash

su -c "source /usr/share/docassemble/local/bin/activate && python -m docassemble.webapp.socketserver" www-data
