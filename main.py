#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import time
from sensor import main_sensor
from server import Server
import sys


def main():
    # Get the node number from the command line argument, which is implemented through sys.argv
    parameter_list = sys.argv # 从命令行参数中获取节点编号，这是通过 sys.argv 实现的

    # 从脚本的命令行参数中获取第二个参数，并将其转换为整数类型, 命令行的第一个参数是main.py/web.py，第二个参数是node_number
    # Get the second parameter from the command line parameter of the script and convert it to an integer type. The first parameter of the command line is main.py/web.py, and the second parameter is node_number.
    node_number = int(parameter_list[1])

    # Set the basic port number to 33335, Open ports: 33000:34000
    basic_port = 33335 # 设置基础端口号为33335，Open ports: 33000:34000

    # Create server name
    server_name = "r"+str(node_number) # 创建服务器名

    # Create a Server object and pass in the necessary parameters
    server = Server(node_number, server_name, basic_port) # 创建一个Server对象，传入必须的参数
    # Start server thread
    server.start() # 启动服务器线程
    # Wait 50 seconds and let the server run for a while
    time.sleep(20) # 等待 50 秒，让服务器运行一段时间
    # Call the main_sensor function to start the sensor (read data from the data table to simulate a real sensor)
    main_sensor(node_number, basic_port) # 调用 main_sensor 函数，启动传感器（从数据表中读入数据，模拟真实的传感器）
    
    # Use server.join() to block the main thread until the server thread terminates, preventing the main program from ending while the child thread is still running.
    server.join() # 使用 server.join() 来阻塞主线程，直到服务器线程终止，防止了主程序在子线程还在运行时就结束了
    # server.join() 确保在程序准备退出之前，服务器线程已经完成了所有的工作。
    # 这是一个常见的模式，特别是在涉及网络服务器的程序中，因为服务器需要持续运行以响应传入的连接。
    # 因此不能在服务器停止运行前就关闭主程序
    # server.join() ensures that the server thread has completed all work before the program is ready to exit.
    # This is a common pattern, especially in programs involving network servers, since the server needs to be running continuously to respond to incoming connections.
    # Therefore, the main program cannot be closed before the server stops running.

if __name__ == '__main__':
    main()
