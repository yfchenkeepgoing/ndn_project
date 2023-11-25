#!/bin/bash

# Define the list of servers and corresponding commands
declare -A servers=(
    ["yijiang@rasp-003.berry.scss.tcd.ie"]="./shell.sh 1"
    ["yangy12@rasp-018.berry.scss.tcd.ie"]="./shell.sh 2"
    ["zhangj20@rasp-012.berry.scss.tcd.ie"]="./shell.sh 3"
    ["welin@rasp-031.berry.scss.tcd.ie"]="./shell.sh 4"
)

# Loop through each server and execute the command
for server in "${!servers[@]}"; do
    command=${servers[$server]}
    echo "Attempting to execute $command on $server"
    if ssh -o StrictHostKeyChecking=no -t $server "cd ndn_project && [ -f ~/.bashrc ] && source ~/.bashrc; nohup $command > /dev/null 2>&1 & sleep 2"; then
        echo "Successfully executed command on $server"
    else
        echo "Failed to execute command on $server"
        exit 1
    fi
done

# Execute the command locally and print output
echo "Executing ./shell.sh 0 locally"
./shell.sh 0

echo "All server commands executed successfully."