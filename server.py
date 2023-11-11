#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import threading # 导入threading模块来支持多线程
import json # 导入json模块来处理JSON数据
import socket # 导入socket模块用于网络通信
import queue # 导入queue模块，提供了同步的、线程安全的队列类
import time # 导入time模块用于处理时间相关的任务
# from interests import INTEREST
from data import DATA
import hashlib # 导入hashlib模块用于加密哈希


BCAST_PORT = 33334 # 定义广播端口为33334

# 定义一个函数来对字符串进行md5哈希，同client.py中的hashstr函数
def hashstr(string):
    md5 = hashlib.md5()
    md5.update(string.encode('utf-8'))
    return md5.hexdigest()

# 定义一个函数来获取本机的IP地址，同web.py中的同名函数
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# 定义Server类，继承自threading.Thread
# 这意味着每个 Server 实例可以作为一个独立的线程运行，这在处理并发网络请求时非常有用
class Server(threading.Thread):

    # 初始化函数
    def __init__(self, serverID, server_name, basic_port):
        # 初始化Server类的父类threading.Thread
        threading.Thread.__init__(self)

        # 获取并设置服务器的IP地址
        self.HOST = get_host_ip()

        self.basic_port = basic_port # 基础端口

        # 根据serverID计算实际端口
        self.PORT_accept = self.basic_port + serverID

        # 创建字典记录服务器的IP地址和实际端口
        self.ip_addr = {server_name: [self.HOST, self.PORT_accept]}
        
        # 点字典，可能用于记录网络中的其他节点
        self.point_dict = {}

        # 存储服务器ID，可能用于区分不同的服务实例
        self.serverID = serverID  # 这个就是循环对应的数据产生的端口
        
        # 存储服务器的名称
        self.server_name = server_name

        # 网络字典，可能用于记录整个网络的拓扑或状态
        self.net_work = {}

        # 可能定义了队列大小或某种资源的数量上限。
        self.sizes = 100

        # FIB (Forwarding Information Base) 字典，用于存储路由信息
        self.fib = {}

        # 用于存储数据的字典
        self.data_dict = dict()

        # 利用 queue 模块创建一个队列，用于存放接收到的 "interest" 请求。
        self.interest_queue = queue.Queue(self.sizes)    # queue.Queue()
        
        # 定义了一个内容数量的限制或者是提供的内容数量
        self.content_num = 100  # 这个就是信息的数量
        
        # class objects
        # 创建了 INTEREST 和 DATA 的实例，这些可能是处理网络兴趣包和数据包的类
        # self.interest = INTEREST()
        self.data = DATA()

    # 在 Python 中，当你创建一个线程时，你通常会从 threading.Thread 类派生一个新类，并且重写该类的 run() 方法。
    # run() 方法定义了线程启动后将要执行的操作。当你调用线程的 start() 方法时，它会在新的线程中调用 run() 方法。
    def run(self):
        # run 方法会被线程启动时调用。
        # 创建了几个线程分别处理不同的任务。
        accept = threading.Thread(target=self.accept)  
        broadcast_iP = threading.Thread(target=self.broadcastIP)  
        update_list = threading.Thread(target=self.updateList)  
        interests = threading.Thread(target=self.interests_process) 
        
        # 启动上述创建的线程
        broadcast_iP.start()
        update_list.start()
        accept.start()
        interests.start()
        time.sleep(10)

        # 主线程等待这些辅助线程完成
        accept.join()
        interests.join()

    # 构建环状的网络拓扑，定义了网络中每个节点的邻居节点
    # self.point_dict 包含网络中所有节点的信息，而 self.net_work 字典将每个节点标识（例如 'r0', 'r1' 等）映射到该节点的邻居节点标识的列表。
    # 这个方法保证了每个节点至少有两个邻居，即便在网络的边缘（第一个和最后一个节点）。这种网络拓扑可能是用来模拟一个环形网络，其中每个节点都连接到它的前一个和后一个节点
    def get_network(self):
        # 遍历点字典，这个字典包含网络中所有节点的信息
        for i in range(len(self.point_dict)):

            # 如果是最后一个节点，它的邻居被设置为第一个节点和倒数第二个节点。
            # 这样做可能是为了形成一个闭环，使得网络中的每个节点都是连通的。
            # 如果网络中只有一个节点，则它的邻居只有它自己
            if i == len(self.point_dict) - 1:
                self.net_work['r' + str(i)] = {0, i - 1} if i >= 1 else {0} # 条件表达式，它根据当前迭代的索引i来设置网络中节点的邻居节点
                # 结束循环，因为已经添加了最后一个节点
                break
            
            # 如果是第一个节点，它的邻居被设置为第二个节点和最后一个节点
            elif i == 0:
                self.net_work['r' + str(i)] = {i + 1, len(self.point_dict) - 1}
            
            # 对于网络中的中间节点，邻居被设置为前一个和后一个节点
            else:
                self.net_work['r' + str(i)] = {i - 1, i + 1}
        
        # 这个循环将邻居节点的集合转换为列表。
        # 这可能是因为列表比集合更容易索引和操作。
        for k, v in self.net_work.items():
            self.net_work[k] = list(v)

    # 构建 FIB 表（转发信息库），确定数据包的转发路径
    # FIB是命名数据网络（NDN）中的一个关键概念，用于决定兴趣包（interest packets）如何在网络中转发
    # 旨在逐层构建出一个从源节点到网络中每个其他节点的最短路径映射
    # 在每次迭代中，upper_layer 包含的节点被用来探索新的节点（即它们的邻居），并确定这些新节点的下一跳（即它们在 FIB 中的值）。这样做可以确保网络中每个节点都可以通过最短路径到达源节点
    def get_fib(self):
        try:
            # 初始化一个空集合，用来存放已经处理过的节点
            key_set = set()

            # 获取网络中所有节点的集合
            key_whole_set = set(self.net_work.keys())

            # 初始化包含当前服务器ID的节点列表，这将作为信息传播的起点
            # 第一次迭代中，upper_layer是源节点（服务器自身）
            # upper_layer: 表示当前考虑的节点的集合，在第一次迭代中，它包含的是源节点（通常是服务器自身）。
            # 这些节点被视为当前“层”或者搜索的当前“前沿”，在这个前沿中，每个节点都将被用来搜索它们的邻居节点。
            # new_layer: 当从 upper_layer 的每个节点扩展搜索到它们的邻居时，这些新发现的邻居节点被添加到 new_layer 中。
            # 在每次迭代结束时，new_layer 包含了下一层的节点，这些节点将在下一次迭代中成为新的搜索前沿。
            upper_layer = ['r' + str(self.serverID)]

            # 初始化计数器，用于避免可能的无限循环
            a = 0

            # 分层的广度优先搜索
            # 如果还有未处理的节点，继续循环
            # 这个过程重复进行，直到所有节点都被探索过，并且它们的下一跳都被添加到 FIB 中。这个方法可以确保在无向图或者有向无环图中，
            # 从源节点到每个节点都有一条路径。在信息中心网络中，这样的 FIB 对于指导兴趣包（interest packets）从一个节点传输到请求数据的节点是必要的
            while key_set < key_whole_set:
                a += 1 # 自增计数器

                # 如果计数器超过40，退出循环以防止潜在的无限循环
                if a > 40:
                    break
                
                # 新的层级，用于存储这一轮被处理的节点
                new_layer = []

                # 对于未处理的节点（key_whole_set - key_set 计算差集）
                for key in key_whole_set - key_set:
                    for i in upper_layer: # 遍历上一层的节点
                        # 如果当前节点就是上层节点，或者上层节点是当前节点的邻居
                        if key == i or int(i.strip('r')) in self.net_work[key]:
                            # 在FIB中为当前节点设置转发路径到上层节点
                            self.fib[key] = i
                            # 将当前节点添加到已处理的节点集合中
                            key_set.add(key)
                            # 将当前节点添加到新的层级中，它可能会成为下一轮的上层节点
                            new_layer.append(key)
                # 更新上层节点为这一轮处理的新层节点
                upper_layer = new_layer
        except Exception as e: # 异常处理
            pass

    # 使用 UDP 广播服务器的 IP 地址和端口号
    # UDP 协议是一个无连接的协议，这意味着数据包（在这种情况下是IP地址）被发送到网络中，而不需要建立和维护一个持续的连接。
    # 由于这个原因，UDP通常用于广播和多播通信。在这个特定的上下文中，每10秒服务器就会广播一次它的IP地址，这样其他设备就可以知道它的存在，并且在需要的时候可以与它通信
    def broadcastIP(self):
        # # 创建一个新的socket对象，使用IPv4(AF_INET)，UDP协议(SOCK_DGRAM)，IPPROTO_UDP指明了使用UDP
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # 这里创建的是UDP协议
        
        # 设置socket的选项，启用广播模式
        # SOL_SOCKET是正在使用的socket选项级别，SO_BROADCAST是指定广播的选项名称，1是选项值，启用广播
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
        
        # 设置socket操作的超时时间为0.5秒
        # 如果sendto或recvfrom在0.5秒内没有完成，会抛出socket.timeout异常
        server.settimeout(0.5)

        # 将服务器的IP地址转换为JSON格式的字符串，然后编码为UTF-8字节串准备发送
        message = json.dumps(self.ip_addr).encode('utf-8')
        
        # 无限循环，这意味着服务器会不停地发送广播
        while True:
            # 使用sendto方法发送编码后的消息
            # 消息被发送到特殊的'<broadcast>'地址，这是一个广播地址，消息将被发送给所有在BCAST_PORT端口监听的设备
            server.sendto(message, ('<broadcast>', BCAST_PORT))  # 像所有的人广播自己IP
            
            # 休眠10秒，这个休眠时间决定了广播的间隔
            time.sleep(10)

    # 监听广播消息，并更新节点信息字典
    # 这个函数的主要目的是维护网络中的节点信息，它监听广播消息并更新服务器的本地网络拓扑。
    # 通过这样做，服务器能够跟踪网络中的其他节点，并根据这些信息更新其路由决策。这对于在动态变化的网络环境中维持有效的通信至关重要
    def updateList(self):
        # 服务器名称字段下存储了自身的IP和端口信息
        self.point_dict[self.server_name] = (self.HOST, self.PORT_accept)
        
        # 创建一个UDP协议
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  
        
        # 设置socket的选项，以便在socket关闭后立即重新使用端口
        # SO_REUSEPORT允许多个应用程序绑定到同一端口，用于负载均衡
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        
        # 一般在发送UDP数据报的时候，希望该socket发送的数据具有广播特性
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # 绑定socket到一个空字符串表示的地址和BCAST_PORT端口
        # 这样设置是为了监听所有接口上的这个端口的广播消息
        client.bind(("", BCAST_PORT))   

        # 初始化一个计数器，用于周期性地打印网络状态信息
        count_i = 0

        # 无限循环，这意味着服务器会不停地监听广播消息
        while True:
            count_i += 1 # 更新计数器

            # 接收从网络上的任意源发来的最大1024字节的数据
            data, _ = client.recvfrom(1024)

            # 解码并将接收到的JSON格式的数据转换成Python字典
            data = json.loads(data.decode('utf-8'))

            # 解包字典，获取发送方的服务器名和地址信息
            # 地址信息包括host和port
            (key, value), = data.items()
            host = value[0]
            port = value[1]
            point = (host, port)

            # 检查接收到的点是否不是自己，并且之前还没有被记录过
            if point != (self.HOST, self.PORT_accept) and key not in self.point_dict.keys():
                # 如果是新点，则加入到点字典中
                self.point_dict[key] = point
                # 更新网络拓扑信息
                self.get_network()

            # 更新转发信息库
            self.get_fib()

            # 每当计数器达到10的倍数时，打印网络信息，帮助调试和监控
            if count_i % 10 == 0:
                print('net_work: {}'.format(self.net_work))
                print('FIB: {}'.format(self.fib))
                print(('point {}'.format(self.point_dict.keys())))
            
            # 休眠10秒，减缓循环速度，减少资源消耗
            time.sleep(10)
    
    # 接收连接并处理兴趣包（interests）和数据包（data）
    # 这个服务器既可以建立服务也可以发送信息
    # 这个函数负责接受和处理来自客户端的不同类型的网络请求，包括接收数据查询请求、处理数据传输，并且在必要时将请求转发到其他节点。
    # 同时，它也负责管理与客户端的连接和服务器资源
    def accept(self):  
        # 创建一个基于IPv4和TCP的socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 将socket绑定到本地主机的接受端口
        server.bind((self.HOST, self.PORT_accept))
        # 开始监听传入的连接请求，最多可以排队等待的连接数为11
        server.listen(11)
        # 开始一个无限循环，等待并处理连接
        while True:
            # 接受一个新的连接
            conn, addr = server.accept() # 这个accept函数是socket中定义的accept函数，conn是服务器端和客户端之间的连接
            # 接收从客户端发送的数据包，大小限制为1024字节
            packet = conn.recv(1024)
            # 将接收的数据包（预期为JSON格式）解码并加载为Python字典
            packet = json.loads(packet.decode('utf-8'))
            # 从数据包中获取'type'字段，决定接下来的处理流程
            Type = packet['type']

            # 如果数据包类型是'interest'，意味着这是一个兴趣包（请求数据）
            if Type == 'interest':
                # 计算内容名称的哈希值
                hash_string = hashstr(packet['content_name'])

                # 将兴趣包存储在data_dict字典中，以哈希值为键
                self.data_dict[hash_string] = packet

                # 打印接收信息的日志
                print('node {} receive the information {}'.format(self.server_name, packet['content_name']))
            
            # 如果数据包类型是'data'，意味着这是一个数据包（包含请求的数据）
            elif Type == 'data':
                # 打印数据包内容名称的哈希值
                print(hashstr(packet['content_name']))
                # 如果哈希值在data_dict的键中，说明请求的数据在本地可用
                if hashstr(packet['content_name']) in self.data_dict.keys():
                    # 获取哈希值对应的数据
                    information = self.data_dict[hashstr(packet['content_name'])]
                    # 将数据发送回请求的客户端
                    conn.sendall(json.dumps(information).encode('utf-8'))  # 一次性将整个包发完
                else:
                    # 如果本地没有数据，则准备转发数据包
                    packet_forward = self.data.Send_data(self.net_work[self.server_name], self.fib, packet)
                    # 如果有转发信息
                    if packet_forward:
                        # 创建一个新的socket进行连接
                        serve_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        
                        # 连接到下一个节点
                        serve_check.connect((self.point_dict['r' + str(packet_forward[0])][0], self.basic_port + packet_forward[0]))
                        
                        # 发送数据包
                        serve_check.sendall(json.dumps(packet_forward[1]).encode('utf-8'))
                        
                        # 设置socket超时时间
                        serve_check.settimeout(50)

                        # 收到回复信息
                        information = serve_check.recv(1024)

                        # 解码回复数据
                        information = json.loads(information.decode('utf-8'))
                        
                        # 如果收到回复
                        if information:
                            # 发送数据给原始请求者
                            conn.sendall(json.dumps(information).encode('utf-8'))
                            # 关闭连接
                            conn.close()
                            # 如果回复中包含'content_name'，更新本地数据字典
                            if 'content_name' in information.keys():
                                hash_string = hashstr(information['content_name'])
                                self.data_dict[hash_string] = information
                            # 关闭与下一个节点的连接
                            serve_check.close()

                    # 如果无法转发，则向客户端发送'not found'状态
                    else:
                        information = {
                            'status': 'not found'
                        }
                        conn.sendall(json.dumps(information).encode('utf-8'))
            
            # 如果数据包类型是'sensor'，意味着这是一个来自传感器的数据包
            elif Type == 'sensor':
                # 计算内容名称的哈希值
                hash_string = hashstr(packet['content_name'])
                # 存储传感器数据包
                self.data_dict[hash_string] = packet
                # 包的类型改为interest
                packet['type'] = 'interest'
                # 将这个 packet 放入 interest_queue 队列中”，以便另一个线程可以稍后处理它
                self.interest_queue.put(packet)
                information = {
                    'status': 'node receive information'
                }
                # 将information发送给请求的客户端
                conn.sendall(json.dumps(information).encode('utf-8'))

                # 关闭socket
                conn.close()

    # 处理队列中的兴趣包，将它们转发给网络中的其他节点
    # 这个函数的目的是处理队列中的兴趣包，通过网络将它们转发到关联的其他节点，以查找和检索请求的数据
    def interests_process(self):
        # 无限循环
        while True:
            # 检查队列是否为空，若为空，则继续等待直到有兴趣包到达
            if self.interest_queue.empty():
                continue
            else:
                # 从队列中取出一个兴趣包
                packet = self.interest_queue.get()
                try:
                    # 遍历与当前服务器节点相关联的所有网络节点，环装的网络拓扑结构，r1和r0, r2相关联
                    for i in range(len(self.net_work[self.server_name])):
                        # 为每一个关联节点创建一个新的 TCP socket 连接
                        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        # 与每个节点的指定地址和端口建立连接
                        server.connect((self.point_dict['r'+str(self.net_work[self.server_name][i])][0], self.basic_port + self.net_work[self.server_name][i]))
                        # 将 JSON 格式的兴趣包发送到相应的节点
                        server.sendall(json.dumps(packet).encode('utf-8'))
                        # 异常处理
                        server.close()
                except Exception as e:
                    pass

# 兴趣包的结构
"""
{'type': 'interest', 'interest_ID': '20000', 'content_name': 'r6/91'}
"""

# 补充知识
# 在信息中心网络（Information Centric Networking, ICN）和特别是在命名数据网络（Named Data Networking, NDN）中，网络兴趣包（interest packets）和数据包（data packets）是核心的概念。它们的作用如下：

# 网络兴趣包（Interest Packets）
# 内容请求：兴趣包用来表达对数据的需求。它包含了请求特定数据的名称，如一个文件、视频流或其他数据。
# 路由：它们根据命名数据而不是端点地址（如IP地址）被路由。这意味着网络设备（如路由器）会根据数据的名称来转发兴趣包。
# 去中心化：它允许用户请求内容而不需要知道内容的实际位置，因为网络将负责找到并传送数据回复。
# 缓存：网络中的节点可以缓存数据，使得相同的兴趣包可以被本地缓存的数据满足，降低了对原始数据源的需求和延迟。

# 数据包（Data Packets）
# 内容传输：当一个节点（如服务器或路由器）收到一个兴趣包并且它拥有或者可以获取所请求的数据，它会用数据包响应。
# 验证：数据包通常包含签名或其他形式的验证信息，以确保数据的完整性和来源的真实性。
# 满足请求：数据包是对兴趣包的直接响应，只有当有兴趣包请求时，数据包才会被发送。
# 无状态传输：与传统的IP网络不同，数据包的传输是无状态的，意味着它们不需要预先建立的连接。

# 在ICN/NDN的上下文中，兴趣包和数据包的交互定义了网络通信的方式。发送者不发送数据到特定的地址，而是广播它对特定数据的兴趣。网络中的节点负责正确路由这些兴趣包到数据源，并将数据返回给请求者。这种模式强调了数据本身的重要性，而不是数据的位置或者数据通信的具体终点。
