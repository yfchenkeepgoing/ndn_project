#!/bin/bash

# Define the list of servers
servers=(
    "yijiang@rasp-003.berry.scss.tcd.ie"
    "yangy12@rasp-018.berry.scss.tcd.ie"
    "zhangj20@rasp-012.berry.scss.tcd.ie"
    "welin@rasp-031.berry.scss.tcd.ie"
)

# Loop through each server and execute the terminate command
for server in "${servers[@]}"; do
    echo "Attempting to execute terminate command on $server"
    if ssh -o StrictHostKeyChecking=no -t $server "cd ndn_project && [ -f ~/.bashrc ] && source ~/.bashrc; ./terminate.sh"; then
        echo "Successfully executed terminate command on $server"
    else
        echo "Failed to execute terminate command on $server"
        exit 1
    fi
done

echo "All termination commands executed successfully."
