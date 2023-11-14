#!/usr/bin/python2.6
# -*- coding: utf-8 -*-


class DATA():
    def __init__(self):
        self.data_package = {}

    # Send_data 方法的作用是确定数据包下一个应该转发到的节点，并返回这个信息
    # The function of the Send_data method is to determine the next node to which the data packet should be forwarded and return this information.
    
    # Infaces（可能是代表接口的列表），fib（转发信息基础表，用于决定数据如何在网络中转发），和 data（要发送的数据包）
    # Infaces (may be a list representing interfaces), fib (forwarding information basic table, used to determine how data is forwarded in the network), and data (data packets to be sent)

    def Send_data(self, Infaces, fib, data):
        # 用于存储准备发送的数据包
        # Used to store data packets to be sent
        packets = []

        # 从 data 字典中获取 content_name 字段的值。这个值标识了数据包请求的内容
        # Get the value of the content_name field from the data dictionary. This value identifies the content of the packet request
        content_name = data['content_name']

        # 分割 content_name 字符串，取出第一个元素，它可能代表了数据包目标的路由器或节点的名称
        # Split the content_name string and take out the first element, which may represent the name of the router or node to which the packet is destined.
        content_router = content_name.split('/')[0]
        
        # 检查 content_router 是否在转发信息基础表（FIB）的键中，如果在，说明有路由信息对应这个路由器或节点
        # Check whether content_router is in the key of the forwarding information base table (FIB). If it is, it means that there is routing information corresponding to this router or node.
        if content_router in fib.keys():
        
            # 获得下一个节点的标识符
            # Get the identifier of the next node
            next_node = int(fib[content_router].strip('r'))
            
            # 检查转发到的下一个节点是否在接口列表 Infaces 中，如果在，说明可以向这个接口发送数据
            # Check whether the next node forwarded to is in the interface list Infaces. If it is, it means that data can be sent to this interface.
            if next_node in Infaces:
                
                # 函数返回一个列表，包含下一个节点的标识符和数据包
                # The function returns a list containing the identifier and data packet of the next node
                return [next_node, data]
        
        # 如果没有找到合适的下一个节点，函数返回一个空的 packets 列表
        # If no suitable next node is found, the function returns an empty packets list
        return packets

