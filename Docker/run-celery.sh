#!/bin/bash

source /usr/share/docassemble/local/bin/activate

exec celery worker -A docassemble.webapp.worker --loglevel=INFO
