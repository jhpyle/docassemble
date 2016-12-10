#!/bin/bash

source "${DA_PYTHON:-/usr/share/docassemble/local}/bin/activate"

exec celery worker -A docassemble.webapp.worker --loglevel=INFO
