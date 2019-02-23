#!/usr/bin/env bash

cd "$(dirname "$0")"
if [ "$#" != "1" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 PORT|debug"
    exit 1
fi

if [ "$1" = "debug" ]; then
    .venv/bin/sbserver
else
    .venv/bin/gunicorn -w 4 -b "0.0.0.0:$1" --access-logfile "access.log" sbserver:app
fi
