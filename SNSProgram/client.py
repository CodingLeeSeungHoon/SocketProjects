import socket
import json

HOST = '172.30.1.59'
PORT = 9132

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# 새로운 계정 생성 테스트용 Dictionary
json_data = {
    'function_id': 1,
    'user_id': '승훈',
    'user_pw': '1234'
}

# 로그인 시도 테스트용 Dictionary
json_data2 = {
    'function_id': 2,
    'user_id': '승훈',
    'user_pw': '1234'
}

# 게시물 확인 테스트용 Dictionary
json_data3 = {

}

# 게시물 업로드 테스트용 Dictionary
json_data4 = {

}

# 팔로우 테스트용 Dictionary
json_data5 = {
    'function_id': 5,
    'user_id': 'andy',
    'follow_id': 'han'
}

# 팔로우 목록 확인 테스트용 Dictionary
json_data6 = {
    'function_id': 6,
    'user_id': 'andy'
}

# 로그아웃 테스트용 Dictionary
json_data7 = {
    'function_id': 7,
    'user_id': 'andy'
}

while True:
    message = input('Enter Message : ')
    if message == 'quit':
        break
    elif message == 'send':
        message = json.dumps(json_data)
    elif message == 'send2':
        message = json.dumps(json_data2)
    elif message == 'send3':
        message = json.dumps(json_data3)
    elif message == 'send4':
        message = json.dumps(json_data4)
    elif message == 'send5':
        message = json.dumps(json_data5)
    elif message == 'send6':
        message = json.dumps(json_data6)
    elif message == 'send7':
        message = json.dumps(json_data7)

    client_socket.send(message.encode())
    data = client_socket.recv(1024)
    print('Received from the server :', repr(json.loads(data.decode())))


client_socket.close()

