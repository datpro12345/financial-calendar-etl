#!/bin/sh
set -e
cd /app

if [ "$#" -eq 0 ]; then
  set -- python scripts/run_weekly_abcd.py --fmt csv
fi

exec "$@"
