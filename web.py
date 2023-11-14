# web.py的作用：
# 创建一个flask应用实例：作用是生成一个可供展示的网页
# 通过创建socket监听了本地的POD_PORT端口，并向该端口发送clientMessage，并返回本地的POD_PORT端口的返回值
# 在此过程中，本地扮演的角色是服务器（本地是NDN的一个节点，既可以扮演服务器也可以扮演客户端）
# 这相当于根据clientMessage中包含的信息在本地查找相应的结果，然后返回值显示在网页上
# 实现将返回值显示在网页上的函数是：app.add_url_rule('/<string:city>/<string:weather>', view_func=client)
# client函数需要的两个参数city和weather由url中对应city和weather的部分传入
# web.py中的POD_PORT是返回查询结果的端口，初始编号是33335，web_basic_port是网页上需要访问的端口，初始编号是33350

#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import socket # 导入用于网络操作的库socket, socket的中文就是套接字
import json # 用于处理json数据格式
import time # 用于获取和格式化时间信息
import sys # 用于访问由命令行传递的参数
from flask import Flask # 导入flask框架中，用于创建web应用
# web_basic_port: Flask web 应用的监听端口（在本地）
# POD_PORT: 客户端和本地通信的端口号（也在本地）
# 这对于分布式应用或在同一台机器上运行多个实例的情况非常有用


app = Flask(__name__) # 创建一个flask应用实例
POD_HOST = '0.0.0.0' # 定义了flask应用的主机地址，设置为0.0.0.0
# 意味着 Flask 应用将在服务器的所有网络接口上监听传入的连接
# 使得flask应用可以从网络中的任何其他机器上被访问，而不仅仅是运行 Flask 应用的本地机器

# 定义获取当前主机在网络上的IP地址的函数
# 本函数的作用是确定哪个IP地址将用于与外部世界通信，或者说获取可用于出站连接的本地IP地址
# 这在有多个网络接口（例如WIFI和以太网）的系统上很有用
# “欺骗”操作系统，让它展露处用于向指定目标发送数据的本地IP地址
def get_host_ip():
    try:
        # socket模块用于网络通信
        # socket.AF_INET指定了地址族为IPv4
        # socket.SOCK_DGRAM 表明s使用的是 UDP 协议
        # 使用UDP协议的原因是不需要再获取本地IP地址时与远程服务器建立一个实际的连接
        # s = socket.SocketType(family = socket.AF_INET, type = socket.SOCK_DGRAM)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 将创建的UDP格式的s连接到远程地址8.8.8.8（google的公共DNS服务器）的80端口
        # 这里的connect实际上并不会建立一个真正的UDP连接，因为UDP是无连接的
        # 它仅仅设置了远程目标的 IP 地址和端口号，以便于 getsockname 能够获取到用于该连接的本地 IP 地址
        s.connect(('8.8.8.8', 80))

        # 这行代码获取了s绑定的本地IP地址。由于s尝试连接到外部地址，getsockname返回的僵尸主机用于出站通信的IP地址
        ip = s.getsockname()[0]

    # 清理资源，关闭s，释放了与s相关的系统资源
    finally:
        s.close()

    return ip # 返回获取到的本地IP

# 定义处理城市和天气请求的客户端函数
# 本函数的作用是将city, weather和time信息由本地通过TCP协议传输到服务器端，并返回服务器端发送回来的字符串
def client(city, weather):
    # 创建字典clientMessage
    # 'type': 'data'：这个字典包含的是数据类型
    # content_name是一个格式化的字符串，包含了city, weeather，以及当前的日期和小时
    # 日期和小时通过time.strftime("%Y-%m-%d %H", time.localtime()) 格式化获得的，它会返回当前时间的年月日和小时
    clientMessage = {'type': 'data',
                     'content_name': '{}/{}/{}'.format(city, weather, time.strftime("%Y-%m-%d %H", time.localtime()))}
    
    # client = socket.SocketType(family = socket.AF_INET, type = socket.SOCK_STREAM)
    # client采用的是TCP协议，用于IPv4网络通信
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 设置了client的一个选项，允许在同一个地址上重用套接字地址（即使之前的套接字还没有完全关闭）。这对于快速重启在相同端口上的服务器是有用的。
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 使客户端套接字连接到由 get_host_ip() 返回的IP地址和 POD_PORT 端口上的服务器。get_host_ip() 函数的目的是获取当前主机的IP地址。
    client.connect((get_host_ip(), POD_PORT))
    
    # 将 clientMessage 字典转换为 JSON 格式的字符串，并将其编码为 UTF-8 格式的字节串，然后通过 TCP 套接字发送给服务器
    client.sendall(json.dumps(clientMessage).encode('utf-8'))
    
    # 接收服务器发送回来的数据。client.recv(1024) 接收最多1024字节的数据。
    # 然后，接收到的字节串被解码为 UTF-8 格式的字符串，并使用 json.loads 解析为一个 Python 字典（假设服务器发送的是 JSON 格式的响应）
    serverMessage = json.loads(client.recv(1024).decode('utf-8'))
    
    # 关闭服务器套接字，释放相关的资源
    client.close()
    
    # 返回了从服务器接收到的消息，该消息现在存储在 serverMessage 字典中
    return serverMessage

# 定义web服务器的主函数, web_basic_port指定了Flask 应用将要监听的端口号
def web_main(web_basic_port):
    # 向 Flask 应用添加了一个 URL 规则
    # add_url_rule 方法用于手动绑定一个 URL 到一个视图函数
    # '/<string:city>/<string:weather>' 指定了两个动态部分：city 和 weather，它们都是字符串类型。
    # 当一个请求匹配到这个模式时，例如 /Berlin/sunny，city 和 weather 将被捕获并作为参数传递给 client 函数
    # view_func=client 表明当请求这个 URL 模式时，应该调用 client 函数来处理请求
    app.add_url_rule('/<string:city>/<string:weather>', view_func=client)
    
    # 启动flask应用
    # host=POD_HOST 设置了主机地址，POD_HOST 设为 '0.0.0.0' 表示监听所有公共 IP 地址
    # 也就是说，无论请求来自主机的哪个网络接口（无论是本地回环地址 127.0.0.1、局域网地址还是公网地址），只要数据包到达了该服务监听的端口，服务都会处理这个请求
    # port=web_basic_port 意思是flask应用通过web_basic_port端口监听进入的所有请求
    # debug=True为发生错误时提供调试界面
    app.run(host=POD_HOST, port=web_basic_port, debug=True)


# 当前脚本如果作为主程序执行，则执行以下的代码
# 这段代码允许你启动多个 Flask 实例，每个实例监听不同的端口号，这些端口号基于节点号 node_number 来确定。这样的设置可能用于一个分布式系统或者多个独立的服务在同一台机器上运行的情况。
# ./web.py就会执行以下部分
if __name__ == '__main__':
    # 获取命令行参数的列表，并将其赋值给变量parameter_list
    parameter_list = sys.argv 
    node_number = int(parameter_list[1]) # 将传入的参数赋给节点编号
    web_basic_port = 33351 # flask应用通过本端口来监听请求
    POD_PORT = 33335 # 客户端和本地通过此端口进行通信

    # 不同的节点可以在不同的端口上和运行，防止端口冲突
    web_basic_port += node_number

    # 每个节点都有一个独特的端口号进行通信
    POD_PORT += node_number

    # 调用web_main函数，传入计算后的端口以启动flask应用
    web_main(web_basic_port)



# curl http://127.0.0.1:33351/r1/temperature

