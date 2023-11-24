#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
import json
import socket
import pandas as pd
import threading
import time
from utils import get_host_ip, encrypt_with_aes, decrypt_with_aes
import random
from typing import List


class Client(threading.Thread):
    '''
    Client class; extends to multi-threading mode
    '''
    agri_dict = {
        0: ('temperature', '°C'),
        1: ('humidity', '%rh'),
        2: ('cec', 'meq/100g'),
        3: ('compaction', 'g/cm3'),
        4: ('nutrition', '%'),
        5: ('pH', ''),
        6: ('salinity', 'dS/m'),
        7: ('pesticides', 'ppm')
    }

    def __init__(self, serverID: int, index: int, basic_port: int):
        threading.Thread.__init__(self)
        self.basic_port = basic_port
        self.HOST = get_host_ip()
        self.PORT = self.basic_port + serverID
        self.serverID = serverID  
        self.index = index
        self.df = pd.read_csv("sensor/{}.csv".format(self.serverID+1))


    def run(self) -> None:
        '''
        Function to define the operations after the thread is started.

        Initializes and starts multiple threads for different weather data types.
        Each thread handles a sensor, calling the start_client() function.
        '''
        client_list = []
        for i in range(8):
            # Get the data of the corresponding column from the data frame
            informations = self.df.iloc[:, i]
            # Create a thread, the target function is start_client, pass in the data type index and data
            client = threading.Thread(target=self.start_client, args=(i, informations, self.index))
            client.start()
            # Add thread to client list
            client_list.append(client)
        # Wait for all threads to complete
        for i in client_list:
            i.join()


    def start_client(self, i: int, informations: List, index: int) -> None:
        '''
        Start the client to send sensor data to the server.

        Params:
            i (int): Index representing the weather data type.
            informations (List): List of weather data information.
            index (int): Index of the data.
        '''
        clientMessage = {
            'type': 'sensor',
            'content_name': 'r{}/{}/{}'.format(self.serverID, self.agri_dict[i][0], time.strftime("%Y-%m-%d %H", time.localtime())),
            'information': str(informations[random.randint(1, len(informations)-1)]),
            'sensor_type': self.agri_dict[i][0],
            'unit': self.agri_dict[i][1],
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        try:
            # Create a TCP socket and connect to the server
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client.connect((self.HOST, self.PORT))
            print(f"Publishing sensor data for {self.agri_dict[i][0]}.....")

            # Send weather information to local, ensure_ascii=False for sending correct units
            client.sendall(encrypt_with_aes(json.dumps(clientMessage, ensure_ascii=False).encode('utf-8')))

            # The information returned by the local after receiving the weather information
            serverMessage = str(decrypt_with_aes(client.recv(1024)), encoding='utf-8')
        except Exception as e:
            print(f"Error in TCP Connection: {e}")
        finally:
            client.close()


def main_sensor(serve_number: int, basic_port: int) -> None:
    '''
    Function to pass in the parameters required by all clients. 
    It is essentially a management function for all clients.
    '''
    for index in range(1500):
        client = Client(serve_number, index, basic_port)
        client.start()
        time.sleep(20)
