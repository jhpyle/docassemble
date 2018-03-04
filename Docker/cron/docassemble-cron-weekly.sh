#! /bin/bash

export CONTAINERROLE=":${CONTAINERROLE:-all}:"

if [ "${S3ENABLE:-null}" == "null" ] && [ "${S3BUCKET:-null}" != "null" ]; then
    export S3ENABLE=true
fi

if [ "${S3ENABLE:-null}" == "true" ] && [ "${S3BUCKET:-null}" != "null" ] && [ "${S3ACCESSKEY:-null}" != "null" ] && [ "${S3SECRETACCESSKEY:-null}" != "null" ]; then
    export AWS_ACCESS_KEY_ID=$S3ACCESSKEY
    export AWS_SECRET_ACCESS_KEY=$S3SECRETACCESSKEY
fi

if [ "${AZUREENABLE:-null}" == "null" ] && [ "${AZUREACCOUNTNAME:-null}" != "null" ] && [ "${AZURECONTAINER:-null}" != "null" ]; then
    export AZUREENABLE=true
fi

if [[ $CONTAINERROLE =~ .*:(all|cron):.* ]]; then
    /usr/share/docassemble/webapp/run-cron.sh cron_weekly
fi
