from socket import *
from threading import Thread

PORT = 6000
ADDRESS = '127.0.0.1'

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((ADDRESS, PORT))

def listen_to_server(socket):
    while True:
        message = socket.recv(1024).decode()
        print(message)

thread = Thread(target=listen_to_server, args=[client_socket])
thread.start()

while True:
    from_console = input()
    client_socket.send(from_console.encode())
