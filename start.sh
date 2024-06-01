#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
PID_FILE="$SCRIPT_DIR/streamlit_server.pid"

PYTHONDONTWRITEBYTECODE=1

if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    kill -0 $pid 2> /dev/null
    if [ $? -eq 0 ]; then
        echo "Process already running"
        exit 1
    fi
fi

cd $SCRIPT_DIR

set | sed 's/^/SET: /'
env | sed 's/^/ENV: /'

python -m invoke run < /dev/null > nohup.out 2>&1 &

pid=$!
echo $pid > "$PID_FILE"
