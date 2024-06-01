#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
PID_FILE="$SCRIPT_DIR/streamlit_server.pid"

if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    kill -0 $pid 2> /dev/null
    if [ $? -ne 0 ]; then
        echo "Server is not running"
        exit 1
    fi
fi

echo "Stopping server"
kill $(cat "$PID_FILE")

echo "Removing PID file"
rm "$PID_FILE"

echo "Done."