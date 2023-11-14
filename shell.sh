#!/bin/bash
echo hello world!
# 这一行在后台启动 main.py 脚本，并传递一个参数（$1），这个参数在执行 shell.sh 脚本时给出。
# 例如，如果执行 ./shell.sh 0，那么 main.py 会接收到 0 作为参数。
# This line starts the main.py script in the background and passes an argument ($1) that is given when the shell.sh script is executed.
# For example, if you execute ./shell.sh 0, then main.py will receive 0 as an argument.
(python3 ./main.py $1)&
# 这一行同样在后台启动 web.py 脚本，并传递相同的参数
# This line also starts the web.py script in the background and passes the same parameters
(python3 ./web.py $1)&

# 在这个脚本中，使用了 & 符号，这意味着 main.py 和 web.py 将并行运行，而不是顺序执行。
# 这使得能够同时启动主程序和web服务，并让它们在不同的进程中运行
# In this script, the & symbol is used, which means that main.py and web.py will run in parallel instead of sequentially.
# This enables starting the main program and the web service at the same time and having them run in different processes
