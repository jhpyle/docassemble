#!/bin/bash

export DA_UNOSERVER="/usr/bin/unoserver"

set -- $LOCALE
export LANG=$1

export HOME=/var/www

${DA_UNOSERVER}
