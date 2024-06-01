#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
PID_FILE="$SCRIPT_DIR/streamlit_server.pid"

if [ -f "$PID_FILE" ]; then
    echo "PID file exists"
    pid=$(cat "$PID_FILE")
    kill -0 $pid 2> /dev/null
    if [ $? -eq 0 ]; then
        echo "Server is running"
        exit 0
    else
        echo "Server is not running"
        exit 1
    fi
else
    echo "PID file does not exist"
    exit 1
fi
