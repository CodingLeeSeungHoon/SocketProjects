import socket
from _thread import *
import json
from server_function import *

# 쓰레드에서 실행되는 코드입니다.
class Server:
    def __init__(self, host, port):
        self.__HOST = host
        self.__PORT = port
        self._server_socket = None
        self.sm = ServerManager()

    def get_server_host(self):
        return self.__HOST

    def get_server_port(self):
        return self.__PORT
    
    def server_init(self):
        print("Server Start!")
        if self._server_socket is None:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((self.__HOST, self.__PORT))
            self._server_socket.listen(10)

    def process(self):
        while True:
            print('Waiting for new client')

            client_socket, addr = self._server_socket.accept()
            start_new_thread(self.threaded, (client_socket, addr))

    def close_server(self):
        self._server_socket.close()

    def threaded(self, client_socket, addr):
        print('Connected by :', addr[0], ':', addr[1])

        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    print('Disconnected by ' + addr[0], ':', addr[1])
                    break
                print(data)
                raw_data = data.decode("cp949")
                command = json.loads(raw_data)

                if command['function_id'] == 1:
                    print('Received from ' + addr[0], ':', addr[1], "/ 회원가입 요청")
                    data = self.sm.add_new_account(command)

                elif command['function_id'] == 2:
                    print('Received from ' + addr[0], ':', addr[1], "/ 로그인 요청")
                    data = self.sm.login(command)

                elif command['function_id'] == 3:
                    print('Received from ' + addr[0], ':', addr[1], "/ 게시물 전달 요청")
                    data = self.sm.return_posts(command)

                elif command['function_id'] == 4:
                    print('Received from ' + addr[0], ':', addr[1], "/ 게시물 업로드 요청")
                    data = self.sm.write(command)

                elif command['function_id'] == 5:
                    print('Received from ' + addr[0], ':', addr[1], "/ 팔로우 요청")
                    data = self.sm.follow(command)

                elif command['function_id'] == 6:
                    print('Received from ' + addr[0], ':', addr[1], "/ 팔로우 목록 전달 요청")
                    data = self.sm.get_follow_list(command)

                elif command['function_id'] == 7:
                    print('Received from ' + addr[0], ':', addr[1], "/ 로그아웃 요청")
                    data = self.sm.logout(command)

                client_socket.send(data.encode())

            except ConnectionResetError as e:
                print('Disconnected by ' + addr[0], ':', addr[1])
                break

        client_socket.close()


server = Server('172.30.1.59', 9132)
server.server_init()
server.process()
server.close_server()
