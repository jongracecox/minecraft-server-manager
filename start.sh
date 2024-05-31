#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
PID_FILE="$SCRIPT_DIR/streamlit_server.pid"
PYTHON="venv/bin/python3"
HOME="/Users/$USER"

#PATH=/opt/homebrew/opt/openjdk/bin:/Users/jongracecox/Library/Python/3.9/bin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/opt/homebrew/bin:/usr/local/bin
PATH=/opt/homebrew/opt/openjdk/bin:$PATH:/opt/homebrew/bin:/usr/local/bin
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

${PYTHON} -m invoke run < /dev/null > nohup.out 2>&1 &

pid=$!
echo $pid > "$PID_FILE"
