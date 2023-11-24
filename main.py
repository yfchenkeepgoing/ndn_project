#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
import time
from sensor import main_sensor
from server import Server
import sys


def main() -> None:
    '''
    Function to run the main functionality like starting the server and the sensors.
    The program takes a node number as a command-line argument and creates a server with the name and port.
    '''
    parameter_list = sys.argv
    node_number = int(parameter_list[1])

    # Set the basic port number to 33335, Open ports: 33000:34000
    basic_port = 33335

    server_name = "r" + str(node_number)
    server = Server(node_number, server_name, basic_port)
    server.start()
    # Wait 20 seconds and let the server run for a while
    time.sleep(20)
    # Call the main_sensor function to start the sensor
    main_sensor(node_number, basic_port)
    
    # Use server.join() to block the main thread until the server thread terminates, 
    # preventing the main program from ending while the child thread is still running.
    server.join()

if __name__ == '__main__':
    main()
