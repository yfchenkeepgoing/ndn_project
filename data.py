#!/usr/bin/python2.6
# -*- coding: utf-8 -*-


class DATA():
    def __init__(self):
        self.data_package = {}

    # Send_data 方法的作用是确定数据包下一个应该转发到的节点，并返回这个信息
    # Infaces（可能是代表接口的列表），fib（转发信息基础表，用于决定数据如何在网络中转发），和 data（要发送的数据包）
    def Send_data(self, Infaces, fib, data):
        # 用于存储准备发送的数据包
        packets = []
        # 从 data 字典中获取 content_name 字段的值。这个值标识了数据包请求的内容
        content_name = data['content_name']
        # 分割 content_name 字符串，取出第一个元素，它可能代表了数据包目标的路由器或节点的名称
        content_router = content_name.split('/')[0]
        # 检查 content_router 是否在转发信息基础表（FIB）的键中，如果在，说明有路由信息对应这个路由器或节点
        if content_router in fib.keys():
            # 获得下一个节点的标识符
            next_node = int(fib[content_router].strip('r'))
            # 检查转发到的下一个节点是否在接口列表 Infaces 中，如果在，说明可以向这个接口发送数据
            if next_node in Infaces:
                # 函数返回一个列表，包含下一个节点的标识符和数据包
                return [next_node, data]
        # 如果没有找到合适的下一个节点，函数返回一个空的 packets 列表
        return packets

