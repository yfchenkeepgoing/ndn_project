#!/bin/bash

echo Creating Virtual Environment...
python3 -m venv venv
source venv/bin/activate

echo Installing dependencies...
pip3 install -r requirements.txt

echo Creating new tmux session and starting 5 nodes...
tmux new-session -d -s scalable_project_3

# Split the windows
tmux split-window -h
tmux split-window -h
tmux split-window -v
tmux split-window -v

# Select the first pane in the first row and run node 0
tmux select-pane -t 0
tmux send-keys 'python3 ./main.py 0' C-m

# Select the second pane in the first row and run node 1
tmux select-pane -t 1
tmux send-keys 'python3 ./main.py 1' C-m

# Select the third pane in the first row and run node 2
tmux select-pane -t 2
tmux send-keys 'python3 ./main.py 2' C-m

# Select the first pane in the second row and run node 3
tmux select-pane -t 3
tmux send-keys 'python3 ./main.py 3' C-m

# Select the second pane in the second row and run node 4
tmux select-pane -t 4
tmux send-keys 'python3 ./main.py 4' C-m

# Attach to the tmux session
tmux attach-session -t scalable_project_3
