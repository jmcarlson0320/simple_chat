from irc_socket import *
from threading import Thread
from common import *
from irc_message import *

''' associate usernames with sockets '''

PORT = 6000
ADDRESS = '0.0.0.0'

# setup listening socket
server_socket = MyIRCSocket()
server_socket.bind(ADDRESS, PORT)
server_socket.listen()

print('listening on port: ' + str(PORT))

# store all the client sockets
client_sockets = set()

# client socket listener
def listen_to_client(socket):
    while True:
        incomming = socket.recv()
        message = irc_message.from_string(incomming)
        op = message.operation
        if op == CONNECT:
            # handle user connection
            print('connection from username ')
        elif op == LIST_ROOMS:
            # send room list
            print('room list request received')
        elif op == JOIN_ROOM:
            # add user to room
            print('adding user to room ')
        elif op == LEAVE_ROOM:
            # remove user from room
            print('removing user from room')
        elif op == LIST_USERS:
            # send list of users in room
            print('user list request received')
        elif op == CLIENT_SEND_MESSAGE:
            # broadcast message to room
            print('client sending message: ')
        else:
            # uh oh, we don't recognize the message header...
            print('unknown message from client')

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
