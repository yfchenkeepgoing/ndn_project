# sensor.py的主要作用是：
# 读取input2文件夹中所有csv文件中的信息，将其分门别类为8类天气信息，然后将其传输到本地
# 本质上就是模仿了传感器的功能，即收集数据并传给服务器
# The main functions of sensor.py are:
# Read the information in all csv files in the sensor folder, classify it into 8 categories of weather information, and then transfer it to the local
# Essentially, it imitates the function of the sensor, that is, collects data and transmits it to the server

#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import json
import socket
import pandas as pd
import threading
import time
from utils import get_host_ip

"""
Real-time weather broadcast system between cities or countries
1: temperature temperature *
2: Humidity humidity *
3: wind speed *
4: barometic pressure *
5: wind direction
6: Rainfall conditions (sunny, rainy, cloud) weather condition *
7: visibility *
8: Solid pollutants PM2.5 Pollutants
"""

# 定义Client类，开启多线程模式
# Define the Client class and enable multi-threading mode
class Client(threading.Thread):
    # 定义weather字典，将天气数据分为8类
    soil_dict = {
        0: ('temperature', '°C'),
        1: ('humidity', '%rh'),
        2: ('cec', 'meq/100g'),
        3: ('compaction', 'g/cm3'),
        4: ('nutrition', '%'),
        5: ('pH', ''),
        6: ('salinity', 'dS/m'),
        7: ('pesticides', 'ppm')
    }

    # 用于初始化类的函数，主要负责从input2文件夹中的csv文件中读取数据
    # Function used to initialize the class, mainly responsible for reading data from the csv file in the sensor folder
    def __init__(self, serverID, index, basic_port):
        threading.Thread.__init__(self)
        self.basic_port = basic_port
        self.HOST = get_host_ip()
        self.PORT = self.basic_port + serverID
        self.serverID = serverID  
        self.index = index
        # self.df = pd.read_csv("sensor/{}.csv".format(self.serverID+1))
        self.df = pd.read_csv("sensor/{}.csv".format(self.serverID+1))

    # run() 方法定义了线程启动后将要执行的操作
    # The run() method defines the operations to be performed after the thread is started.
    def run(self):
        client_list = []
        # For each weather data type
        for i in range(8):  # 对于每种天气数据类型
            # Get the data of the corresponding column from the data frame
            informations = self.df.iloc[:, i]  # 从数据框中获取对应列的数据

            # 创建一个线程，目标函数是start_client，传入数据类型索引和数据
            #Create a thread, the target function is start_client, pass in the data type index and data
            #Create a server, and the port created each time is directly and randomly specified.
            client = threading.Thread(target=self.start_client, args=(i, informations, self.index))  # 创建服务器, 对于每次创建的端口都是直接随机指定的
            # Start thread
            client.start() # 启动线程
            # Add thread to client list
            client_list.append(client) # 将线程添加到客户端列表

        # 等待所有线程完成
        # Wait for all threads to complete
        for i in client_list:
            i.join()

    # 启动客户端的函数
    # Function to start the client
    def start_client(self, i, informations, index):
        # 构造要发送的消息
        # Construct the message to be sent
        clientMessage = {
            'type': 'sensor',
            'content_name': 'r{}/{}/{}'.format(self.serverID, self.soil_dict[i][0], time.strftime("%Y-%m-%d %H", time.localtime())),
            'information': str(informations[index]) if informations[index] else '',
            'sensor_type': self.soil_dict[i][0],
            'unit': self.soil_dict[i][1],
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        # 创建一个TCP套接字
        # Create a TCP socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 设置套接字选项
        # Set socket options
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # 连接到本机
        # Connect to this machine
        client.connect((self.HOST, self.PORT))
        try:
            # 发送天气信息到本地，ensure_ascii=False 发送正确的单位
            # Send weather information to local, ensure_ascii=False for sending correct units
            client.sendall(json.dumps(clientMessage, ensure_ascii=False).encode('utf-8'))
            
            # 本地在接受到天气信息后返回的信息
            # The information returned by the local after receiving the weather information
            serverMessage = str(client.recv(1024), encoding='utf-8')
            
            # 打印来自server的信息，实际上就是在server.py中定义的"node receive information"
            # Print information from the server, which is actually the "node receive information" defined in server.py
            print('sensor:', serverMessage)
        # 排除掉异常
        # Eliminate exceptions
        except Exception as e:
            pass
        client.close()

# 本函数用于传入所有client所需要的参数，本质是一个所有client的管理函数
# This function is used to pass in the parameters required by all clients. It is essentially a management function for all clients.
def main_sensor(serve_number, basic_port):
    for index in range(500):
        client = Client(serve_number, index, basic_port)
        client.start()
        time.sleep(20)

# 主函数，传入main_sensor所需要的参数
# Main function, pass in the parameters required by main_sensor
if __name__ == '__main__':
    serve_number = 0
    basic_port = 33335
    main_sensor(serve_number, basic_port)
