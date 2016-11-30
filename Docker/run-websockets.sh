#!/bin/bash

source /usr/share/docassemble/local/bin/activate

exec python -m docassemble.webapp.socketserver
