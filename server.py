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
        dispatch_message(message)

def connect(username, socket):
    pass

def list_rooms(message):
    pass

def join_room(message):
    pass

def leave_room(message):
    pass

def list_users(messages):
    pass

def client_send_message(message):
    pass

# unpack and check errors here!
# if errors, dispatch to error handlers
def dispatch_message(message):
    op = message.operation
    if op == CONNECT:
        connect(message)
    elif op == LIST_ROOMS:
        list_rooms(message)
    elif op == JOIN_ROOM:
        join_room(message)
    elif op == LEAVE_ROOM:
        leave_room(message)
    elif op == LIST_USERS:
        list_users(message)
    elif op == CLIENT_SEND_MESSAGE:
        client_send_message(message)
    else:
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
