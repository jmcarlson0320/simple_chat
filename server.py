from socket import *
from threading import Thread

PORT = 6000
ADDRESS = '0.0.0.0'

# setup listening socket
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((ADDRESS, PORT))
server_socket.listen()

print('listening on port: ' + str(PORT))

# store all the client sockets
client_sockets = set()

# client socket listener
def listen_to_client(socket):
    while True:
        message = socket.recv(1024).decode()

        # broadcast the message to all connected clients
        for s in client_sockets:
            s.send(message.encode())

# accept new connections
while True:
    (client_socket, client_address) = server_socket.accept()
    print('new connection from: ' + str(client_address))
    client_sockets.add(client_socket)

    # each client connection is listened to on a different thread
    thread = Thread(target=listen_to_client, args=[client_socket])
    thread.start()

for s in client_sockets:
    s.close()
server_socket.close()
