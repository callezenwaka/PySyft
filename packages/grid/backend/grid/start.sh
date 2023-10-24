#! /usr/bin/env bash
set -e

echo "Running start.sh with RELEASE=${RELEASE}"
export GEVENT_MONKEYPATCH="False"

# For debugging permissions
id
ls -lisa ~/data/

APP_MODULE=grid.main:app
LOG_LEVEL=${LOG_LEVEL:-info}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-80}
RELOAD=""
NODE_TYPE=${NODE_TYPE:-domain}

if [[ ${DEV_MODE} == "True" ]];
then
    echo "DEV_MODE Enabled"
    RELOAD="--reload"
    pip install --user -e "$APPDIR/syft[telemetry]"
fi

set +e
export NODE_PRIVATE_KEY=$(python $APPDIR/grid/bootstrap.py --private_key)
export NODE_UID=$(python $APPDIR/grid/bootstrap.py --uid)
set -e

echo "NODE_UID=$NODE_UID"
echo "NODE_TYPE=$NODE_TYPE"

export NODE_TYPE=$NODE_TYPE

# export GEVENT_MONKEYPATCH="True"
exec uvicorn $RELOAD --host $HOST --port $PORT --log-level $LOG_LEVEL "$APP_MODULE"
