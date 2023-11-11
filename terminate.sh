#!/bin/bash

# Find the process ID of 'python3 ./main.py'
MAIN_PY_PROCESS=$(ps aux | grep 'python3 ./main.py' | grep -v 'grep' | awk '{print $2}')

# Find the process ID of 'python3 ./web.py'
WEB_PY_PROCESS=$(ps aux | grep 'python3 ./web.py' | grep -v 'grep' | awk '{print $2}')

# Initialize a counter for killed processes
KILLED_COUNT=0

# Kill the main.py process
if [ ! -z "$MAIN_PY_PROCESS" ]; then
    echo "Killing process python3 ./main.py with PID $MAIN_PY_PROCESS"
    kill $MAIN_PY_PROCESS
    let KILLED_COUNT++
else
    echo "No process found for python3 ./main.py"
fi

# Kill the web.py process
if [ ! -z "$WEB_PY_PROCESS" ]; then
    echo "Killing process python3 ./web.py with PID $WEB_PY_PROCESS"
    kill $WEB_PY_PROCESS
    let KILLED_COUNT++
else
    echo "No process found for python3 ./web.py"
fi

# Check if both processes were killed
if [ "$KILLED_COUNT" -eq 2 ]; then
    echo "Terminate node successfully."
fi
