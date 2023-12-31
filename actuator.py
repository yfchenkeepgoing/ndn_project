# This file/function was implemented by Smit
import sys
import time
import json
import socket
from utils import get_host_ip, encrypt_with_aes, decrypt_with_aes

POD_PORT = 33335

def get_data(node: str, sensor_type: str):
    '''
    Function to get the requested data from the node
    '''
    try:
        # Construct the message to be sent
        clientMessage = {'type': 'data',
                        'content_name': '{}/{}/{}'.format(node, sensor_type, time.strftime("%Y-%m-%d %H", time.localtime()))}
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.connect((get_host_ip(), POD_PORT))
        client.sendall(encrypt_with_aes(json.dumps(clientMessage).encode('utf-8')))
        serverMessage = json.loads(decrypt_with_aes(client.recv(1024)).decode('utf-8'))
        client.close()
        return serverMessage
    except Exception as e:
        return None

# r1/temperature
requested_data = str(sys.argv[1])
node = requested_data.split('/')[0]
sensor_type = requested_data.split('/')[1]

response = get_data(node, sensor_type)
# Deleting the 'type' key from the response message
if 'type' in response.keys():
    del response['type'] 

print(response)
