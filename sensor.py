# sensor.py的主要作用是：
# 读取input2文件夹中所有csv文件中的信息，将其分门别类为8类天气信息，然后将其传输到本地
# 本质上就是模仿了传感器的功能，即收集数据并传给服务器

#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import json
import socket
import pandas as pd
import threading
import time

"""
城市或者国家之间的实时天气播报系统
Real-time weather broadcast system between cities or countries
1: 温度  temperature   *
2: 湿度  humidity      *
3: 风速  wind speed    *
4: 气压  barometic pressure  *  
5: 风向  wind direction  
6: 降雨情况(sunny, rainy, cloud)  weather condition   *
7: 能见度  visibility   *
8: 固态污染物PM2.5  Pollutants
"""

# 获取本地的IP地址
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# 定义Client类，开启多线程模式
class Client(threading.Thread):
    # 定义weather字典，将天气数据分为8类
    weather_dict = {
        0: ('temperature', '°C'),
        1: ('humidity', '%rh'),
        2: ('wind speed', 'km/h'),
        3: ('barometic pressure', 'millibars'),
        4: ('wind direction', ''),
        5: ('weather condition', ''),
        6: ('visibility', 'km'),
        7: ('pollutants', 'ug/m^3')
    }

    # 用于初始化类的函数，主要负责从input2文件夹中的csv文件中读取数据
    def __init__(self, serverID, index, basic_port):
        threading.Thread.__init__(self)
        self.basic_port = basic_port
        self.HOST = get_host_ip()
        self.PORT = self.basic_port + serverID
        self.serverID = serverID  
        self.index = index
        self.df = pd.read_csv("input2/{}.csv".format(self.serverID+1))

    # run() 方法定义了线程启动后将要执行的操作
    def run(self):
        client_list = []
        for i in range(8):  # 对于每种天气数据类型
            informations = self.df.iloc[:, i]  # 从数据框中获取对应列的数据

            # 创建一个线程，目标函数是start_client，传入数据类型索引和数据
            client = threading.Thread(target=self.start_client, args=(i, informations, self.index))  # 创建服务器, 对于每次创建的端口都是直接随机指定的
            client.start() # 启动线程
            client_list.append(client) # 将线程添加到客户端列表

        # 等待所有线程完成
        for i in client_list:
            i.join()

    # 启动客户端的函数
    def start_client(self, i, informations, index):
        # 构造要发送的消息
        clientMessage = {
            'type': 'sensor',
            'content_name': 'r{}/{}/{}'.format(self.serverID, self.weather_dict[i][0], time.strftime("%Y-%m-%d %H", time.localtime())),
            'information': str(informations[index]) if informations[index] else '',
            'sensor_type': self.weather_dict[i][0],
            'unit': self.weather_dict[i][1],
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        # 创建一个TCP套接字
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置套接字选项
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 连接到本机
        client.connect((self.HOST, self.PORT))
        try:
            # 将天气信息发送给本地
            client.sendall(json.dumps(clientMessage).encode('utf-8'))
            # 本地在接受到天气信息后返回的信息
            serverMessage = str(client.recv(1024), encoding='utf-8')
            # 打印来自server的信息，实际上就是在server.py中定义的"node receive information"
            print('sensor:', serverMessage)
        # 排除掉异常
        except Exception as e:
            pass
        client.close()

# 本函数用于传入所有client所需要的参数，本质是一个所有client的管理函数
def main_sensor(serve_number, basic_port):
    for index in range(500):
        client = Client(serve_number, index, basic_port)
        client.start()
        time.sleep(200)

# 主函数，传入main_sensor所需要的参数
if __name__ == '__main__':
    serve_number = 0
    basic_port = 33335
    main_sensor(serve_number, basic_port)




















