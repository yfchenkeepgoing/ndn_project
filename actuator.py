# This actuator file simulates the below command
# curl http://127.0.0.1:33351/r1/temperature
# curl https://10.35.70.44:33335/r0/temperature
# Run by using the below command
# python3 actuator.py r1/temperature

import sys
import time
import json
import socket
from utils import get_host_ip

POD_PORT = 33335

def get_data(node, sensor_type):
    '''
    Function to get the requested data from the node
    '''
    # Construct the message to be sent
    clientMessage = {'type': 'data',
                     'content_name': '{}/{}/{}'.format(node, sensor_type, time.strftime("%Y-%m-%d %H", time.localtime()))}
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.connect((get_host_ip(), POD_PORT))
    client.sendall(json.dumps(clientMessage).encode('utf-8'))

    # Popping the 'type' key from the response message
    serverMessage = json.loads(client.recv(1024).decode('utf-8')).pop('type')
    client.close()

    return serverMessage

# r1/temperature
requested_data = str(sys.argv[1])

node = requested_data.split('/')[0]
sensor_type = requested_data.split('/')[1]

response = get_data(node, sensor_type)
print(response)
