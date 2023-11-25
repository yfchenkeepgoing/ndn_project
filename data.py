#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
from typing import List, Dict

# This file/function was implemented by Sulaeman
class DataProcessor():
    """
    A class for processing and forwarding data packets in a network.
    """
    def __init__(self):
        self.data_package = {}

    def send_data(self, interfaces: List, fib: Dict, data: Dict) -> List:
        '''
        Function to determine the next node to which the data packet should be forwarded.
        Args:
            interfaces (list): List representing available interfaces.
            fib (dict): Forwarding Information Base (FIB) table.
            data (dict): Data packet to be sent.

        Returns:
            list: A list containing the identifier and data packet of the next node.
            Returns an empty list if no suitable next node is found.
        '''
        packets = []
        # Name of the router/node to which the packet is destined
        content_router = data['content_name'].split('/')[0]

        if content_router in fib:
            # Get the identifier of the next node
            next_node = int(fib[content_router].strip('r'))
            if next_node in interfaces:
                return [next_node, data]
        return packets
