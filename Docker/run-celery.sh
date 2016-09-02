#!/bin/bash

source /usr/share/docassemble/local/bin/activate

celery worker -A docassemble.webapp.worker --loglevel=INFO
