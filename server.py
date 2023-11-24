#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
import threading
import json
import socket
import queue
import time
from data import DataProcessor
from utils import get_host_ip, hashstr, encrypt_with_aes, decrypt_with_aes

BCAST_PORT = 33334

class Server(threading.Thread):
    '''
    Server class; extends to multi-threading mode
    '''
    def __init__(self, serverID, server_name, basic_port):
        threading.Thread.__init__(self)

        # Set a RLock to perform atomic updates 
        self.rlock = threading.RLock()

        # Get and set the IP address of the server
        self.HOST = get_host_ip()
        self.basic_port = basic_port
        # Calculate the actual port based on serverID
        self.PORT_accept = self.basic_port + serverID

        # Time to Live for each node/server in seconds
        self.ttl = 60

        # Create a dictionary to record the IP address, actual port and ttl of the server
        self.ip_addr = {server_name: [self.HOST, self.PORT_accept, self.ttl]}
        self.serverID = serverID
        self.server_name = server_name

        # Point dictionary, used to record other nodes in the network
        self.point_dict = {}

        # Network dictionary, used to record the topology of the network
        self.net_work = {}

        # FIB (Forwarding Information Base) dictionary, used to store routing information
        self.fib = {}

        # Dictionary for storing data
        self.data_dict = dict()

        self.sizes = 100

        # Use the queue module to create a queue to store received "interest" requests.
        self.interest_queue = queue.Queue(self.sizes)

        # Defines a limit on the amount of content or the amount of content provided
        # This is the amount of information
        self.content_num = 100

        # Data class to handle data packets
        self.data = DataProcessor()

        # Broadcast interval in seconds
        self.broadcast_interval = 10


    def run(self) -> None:
        accept = threading.Thread(target=self.accept)
        broadcast_iP = threading.Thread(target=self.broadcastIP)
        update_list = threading.Thread(target=self.updateList)
        decrement_ttl = threading.Thread(target=self.decrement_ttl)
        interests = threading.Thread(target=self.interests_process)
        # Start the thread created above
        broadcast_iP.start()
        update_list.start()
        accept.start()
        interests.start()
        decrement_ttl.start()
        time.sleep(10)
        # The main thread waits for these auxiliary threads to complete
        accept.join()
        decrement_ttl.join()
        interests.join()


    def update_network(self) -> None:
        '''
        Function to build/update the ring-shaped network topology and
        define neighbor nodes for each node.

        This method ensures that each node has at least two neighbors,
        even at the edge of the network, simulating a ring network.
        '''
        # Clear the previous network to avoid stale network
        self.net_work.clear()  
        keys = list(self.point_dict.keys())

        for i in range(len(keys)):
            # If there is only one node in the network, its neighbor is only itself
            if len(keys) == 1:
                self.net_work[keys[0]] = {int(keys[0].strip('r'))}
                break
            # If it is the first node, its neighbors are set to the second node and the last node
            elif i == 0:
                self.net_work[keys[i]] = {int(keys[i + 1].strip('r')), int(keys[-1].strip('r'))}
            # For intermediate nodes in the network, neighbors are set to the previous and next nodes
            elif i == len(keys) - 1:
                self.net_work[keys[i]] = {int(keys[i - 1].strip('r')), int(keys[0].strip('r'))}
            else:
                self.net_work[keys[i]] = {int(keys[i - 1].strip('r')), int(keys[i + 1].strip('r'))}
        # Converting the set of neighbor nodes into a list.
        for k, v in self.net_work.items():
            self.net_work[k] = list(v)


    def update_fib(self) -> None:
        '''
        Function to build/update the Forwarding Information Base (FIB) to 
        determine the forwarding path of data packets using BFS algo.
        '''
        try:
            # Initialize an empty collection to store processed nodes
            key_set = set()

            # Get the set of all nodes in the network
            key_whole_set = set(self.net_work.keys())

            # Removing the stale/inactive nodes
            nodes = list(self.point_dict.keys())
            s = set(self.fib.keys())
            removed_nodes = [x for x in s if x not in nodes]
            for key in list(self.fib.keys()):
                if key in removed_nodes:
                    del self.fib[key]

            # Initialize the node list containing the current server ID, 
            # which will serve as the starting point for information dissemination
            upper_layer = ['r' + str(self.serverID)]
            a = 0

            # Hierarchical breadth-first search in form of layers
            while key_set < key_whole_set:
                a += 1
                # If the counter exceeds 40, exit the loop to prevent a potentially infinite loop
                if a > 40:
                    break

                # New level used to store nodes processed in this round
                new_layer = []
                # For unprocessed nodes (key_whole_set - key_set calculates the difference set)
                for key in key_whole_set - key_set:
                    # Traverse the nodes of the previous layer
                    for i in upper_layer:
                        # If the current node is the upper node, or the upper node is the neighbor of the current node
                        if key == i or int(i.strip('r')) in self.net_work[key]:
                            # Set the forwarding path for the current node in FIB to the upper node
                            self.fib[key] = i
                            # Add the current node to the processed node collection
                            key_set.add(key)
                            # Add the current node to the new level, it may become the upper node of the next round
                            new_layer.append(key)
                # Update the upper layer node to be the new layer node processed in this round
                upper_layer = new_layer
        except Exception as e:
            print(e)
            pass


    def broadcastIP(self) -> None:
        '''
        Function to broadcast the server information on the 'BCAST_PORT' using UDP 
        every 'self.broadcast_interval' seconds. Anyone listening on 'BCAST_PORT' will receive this information.
        '''
        # Create a new socket object, using IPv4 (AF_INET), 
        # UDP protocol (SOCK_DGRAM), IPPROTO_UDP specifies the use of UDP
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # If sendto or recvfrom is not completed within 0.5 seconds, a socket.timeout exception will be thrown
        server.settimeout(0.5)
        while True:
            # Add fresh TTL while sending the broadcast
            self.ip_addr[self.server_name][2] = int(self.ttl)
            # Broadcast self server id,port and host
            message = encrypt_with_aes(json.dumps(self.ip_addr).encode('utf-8'))
            # Broadcast your IP to everyone on 'BCAST_PORT' port
            server.sendto(message, ('<broadcast>', BCAST_PORT))
            # Sleep for 'broadcast_interval' seconds. This sleep time determines the broadcast interval.
            time.sleep(self.broadcast_interval)


    def decrement_ttl(self) -> None:
        '''
        Function to decrement TTL till it reaches zero
        '''
        while True:
            try:
                # acquire the Rlock
                with self.rlock:
                    for key in list(self.point_dict.keys()):
                        # Decrement the TTL
                        temp = list(self.point_dict[key])
                        temp[2] = max(temp[2]-1, 0)
                        self.point_dict[key] = tuple(temp)
            except RuntimeError:
                self.point_dict = {}
            time.sleep(1)


    def updateList(self) -> None:
        '''
        Function to listen to broadcast messages and update the node information dictionary.
        The main purpose is to maintain node information in the network, updating the local network topology of the server.
        This allows the server to track other nodes in the network and update its routing decisions.
        '''
        # The server name field stores its own IP, port and ttl information.
        self.point_dict[self.server_name] = (self.HOST, self.PORT_accept, self.ttl)

        # Create a UDP protocol
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Set options for the socket to reuse the port immediately after the socket is closed
        # SO_REUSEPORT allows multiple applications to bind to the same port for load balancing
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Bind the socket to the address and BCAST_PORT port represented by an empty string
        # This setting is to monitor the broadcast messages of this port on all interfaces.
        client.bind(("", BCAST_PORT))
        while True:
            # Receive data up to 1024 bytes from any source on the network
            data, _ = client.recvfrom(1024)
            data = json.loads(decrypt_with_aes(data).decode('utf-8'))
            (key, value), = data.items()
            host = value[0]
            port = value[1]
            ttl = int(value[2])
            point = (host, port, ttl)

            # Check whether the received point is not itself and has not been recorded before
            if point != (self.HOST, self.PORT_accept, self.ttl) and key not in self.point_dict.keys():
                # If it is a new point, add it to the point dictionary
                self.point_dict[key] = point

            # Updating the point dict to find which node went offline
            with self.rlock:
                keys_to_remove = [key for key in self.point_dict if self.point_dict[key][2] <= 0 and key != self.server_name]
                temp_dict = self.point_dict.copy()
                for key in keys_to_remove:
                    # Ensure the key still exists in the copy
                    if key in temp_dict:
                        del temp_dict[key]
                self.point_dict = temp_dict
                # Update network topology information
                self.update_network()
                # Update forwarding information database
                self.update_fib()

            print('Network: {}'.format(self.net_work))
            print('FIB Table: {}'.format(self.fib))
            print(('Points: {}'.format(self.point_dict.keys())))

            # Sleep for broadcast_interval+1 seconds to slow down the loop speed and reduce resource consumption
            time.sleep(self.broadcast_interval+1)


    def accept(self) -> None:
        '''
        Function to receive connections and process interest packets and data packets.

        This server can both create services and send information.
        This function is responsible for accepting and processing different types of 
        network requests from clients. It includes receiving data query requests, 
        processing data transmission, and forwarding requests to other nodes if necessary.
        '''
        # Create a socket based on IPv4 and TCP
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the local host's accept port
        server.bind((self.HOST, self.PORT_accept))
        # Start listening for incoming connection requests.
        server.listen(11)
        while True:
            # Accept a new connection
            conn, addr = server.accept()
            # Receive data packets sent from the client, the size is limited to 1024 bytes
            packet = conn.recv(1024)
            packet = json.loads(decrypt_with_aes(packet).decode('utf-8'))
            try:
                Type = packet['type']
                # If the packet type is 'interest', it means this is an interest packet (request data)
                if Type == 'interest':
                    # Calculate the hash value of the content name
                    hash_string = hashstr(packet['content_name'])
                    # Store the interest package in the data_dict dictionary, with the hash value as the key
                    self.data_dict[hash_string] = packet
                    # Print the log of received information
                    print('Device {} receive the information {}'.format(self.server_name, packet['content_name']))
                # If the packet type is 'data', it means this is a data packet (containing the requested data)
                elif Type == 'data':
                    # If the hash value is in the key of data_dict, it means that the requested data is available locally.
                    if hashstr(packet['content_name']) in self.data_dict.keys():
                        # Get the data corresponding to the hash value
                        information = self.data_dict[hashstr(packet['content_name'])]
                        # Send data back to the requesting client
                        conn.sendall(encrypt_with_aes(json.dumps(information).encode('utf-8')))
                    else:
                        # If there is no data locally, prepare to forward the data packet
                        packet_forward = self.data.send_data(self.net_work[self.server_name], self.fib, packet)
                        # If there is forwarding information
                        if packet_forward:
                            # Create a new socket to connect
                            serve_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            # Connect to the next node
                            serve_check.connect((self.point_dict['r' + str(packet_forward[0])][0], self.basic_port + packet_forward[0]))
                            # Send packet
                            serve_check.sendall(encrypt_with_aes(json.dumps(packet_forward[1]).encode('utf-8')))
                            serve_check.settimeout(50)
                            # Receive reply message
                            information = serve_check.recv(1024)
                            information = json.loads(decrypt_with_aes(information).decode('utf-8'))
                            if information:
                                # Send data to original requester
                                conn.sendall(encrypt_with_aes(json.dumps(information).encode('utf-8')))
                                conn.close()
                                # If the reply contains 'content_name', update the local data dictionary
                                if 'content_name' in information.keys():
                                    hash_string = hashstr(information['content_name'])
                                    self.data_dict[hash_string] = information
                                # Close the connection to the next node
                                serve_check.close()
                        # If forwarding is not possible, send 'not found' status to client
                        else:
                            information = {
                                'status': 'not found'
                            }
                            conn.sendall(encrypt_with_aes(json.dumps(information).encode('utf-8')))
                # If the packet type is 'sensor', it means this is a packet from a sensor
                elif Type == 'sensor':
                    # Calculate the hash value of the content name
                    hash_string = hashstr(packet['content_name'])
                    # Store sensor data packets
                    self.data_dict[hash_string] = packet
                    # Change the package type to interest
                    packet['type'] = 'interest'
                    # Put this packet into the interest_queue so that another thread can process it later
                    self.interest_queue.put(packet)
                    information = {
                        'status': 'node receive information'
                    }
                    # Send information to the requesting client
                    conn.sendall(encrypt_with_aes(json.dumps(information).encode('utf-8')))
                    conn.close()
            except Exception as e:
                print(f"Something went wrong, dropping the packet due to: {e}")
                continue


    def interests_process(self) -> None:
        '''
        Function to process Interest packets in the queue and forward them through the network to other associated nodes to find and retrieve the requested data.
        '''
        while True:
            # If queue is empty, continue to wait until the interest packet arrives.
            if self.interest_queue.empty():
                continue
            else:
                # Take out an Interest packet from the queue
                packet = self.interest_queue.get()
                try:
                    # Traverse all network nodes associated with current server node
                    for i in range(len(self.net_work[self.server_name])):
                        # Create a new TCP socket connection for each associated node
                        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        # Establish a connection with the specified address and port of each node
                        server.connect((self.point_dict['r'+str(self.net_work[self.server_name][i])][0],\
                                         self.basic_port + self.net_work[self.server_name][i]))
                        # Send the interest packet in JSON format to the corresponding node
                        server.sendall(encrypt_with_aes(json.dumps(packet).encode('utf-8')))
                        server.close()
                except Exception as e:
                    pass
