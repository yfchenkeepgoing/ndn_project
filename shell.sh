# This file/function was implemented by Yifan
#!/bin/bash
echo Starting the Device $1.....
# This line starts the main.py script in the background and passes an argument ($1) that is given when the shell.sh script is executed.
# For example, if you execute ./shell.sh 0, then main.py will receive 0 as an argument.
(python3 ./main.py $1)
