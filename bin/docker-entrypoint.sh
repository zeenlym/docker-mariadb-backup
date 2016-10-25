#!/bin/bash
set -e

if [ -n "$TIMEZONE" ]; then
    echo ${TIMEZONE} > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata
fi

if [ $1 = "go-cron" ]; then

    if [ -z "$SCHEDULE" ]; then
        echo Missing SCHEDULE environment variable 2>&1
        echo 'Example -e SCHEDULE="*/10 * * * * *"' 2>&1
        exit 1
    fi

    if [ -z "$BACKUP_METHOD" ]; then
        echo Missing BACKUP_METHOD environment variable 2>&1
        echo 'Example -e BACKUP_METHOD="mysqldump"' 2>&1
        exit 1
    fi

    exec go-cron -s "${SCHEDULE}" -- /usr/local/bin/backup
fi

exec "$@"

