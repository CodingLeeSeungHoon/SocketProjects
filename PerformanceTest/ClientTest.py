import socket
import json

HOST = '127.0.0.1'
PORT = 9001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
json_data = {
    'function_id': 1,
    'user_id': '승훈',
    'user_pw': '1234'
}

def serial_db_access():
    for i in range(20000):
        message = json.dumps(json_data)
        client_socket.send(message.encode())
        data = client_socket.recv(1024)
        print('Received from the server :', repr(json.loads(data.decode())))
    client_socket.close()


serial_db_access()