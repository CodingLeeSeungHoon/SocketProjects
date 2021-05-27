import socket
from threading import Lock, Thread
from _thread import *
import json
from server_function import *
import time

# 쓰레드에서 실행되는 코드입니다.
class Server:
    def __init__(self, host, port):
        self.__HOST = host
        self.__PORT = port
        self._server_socket = None
        self.sm = ServerManager()
        self.thread_counts = 0
        self.db_access_counts = 0
        self.lock = Lock()
        self.start_time = 0
        self.check_time = []

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
        self.thread_counts += 1
        print("접속한 thread : {}".format(self.thread_counts))

        while True:
            if self.thread_counts == 2:
                self.start_time = time.time()
                break

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
                    self.lock.acquire()
                    data = self.sm.add_new_account(command)
                    self.db_access_counts += 1
                    self.lock.release()

                    print("DB 접근 횟수 : {}".format(self.db_access_counts))
                    if self.db_access_counts % 1000 == 0:
                        self.check_time.append(time.time())

                    if self.db_access_counts == 40000:
                        print([x-self.start_time for x in self.check_time])

                client_socket.send(data.encode())

            except ConnectionResetError as e:
                print('Disconnected by ' + addr[0], ':', addr[1])
                break

        client_socket.close()


server = Server('127.0.0.1', 9001)
server.server_init()
server.process()
server.close_server()
