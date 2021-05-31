from irc_socket import *
from threading import Thread
from common import *
from irc_message import *
from user import *

PORT = 6000
ADDRESS = '0.0.0.0'

# setup listening socket
server_socket = MyIRCSocket()
server_socket.bind(ADDRESS, PORT)
server_socket.listen()

print('listening on port: ' + str(PORT))

# store users in set
users = {}

# setup new connection
def new_connection(socket):
    incomming = socket.recv()
    message = irc_message.from_string(incomming)
    op = message.operation
    argv = message.argv
    argc = message.argc
    if message.operation == CONNECT and message.argc == 1:
        new_user = User(message.argv[0], socket)
        users[new_user.name] = new_user
        print('new connection')
        print('username: ' + message.argv[0])
        listen_to_client(users[message.argv[0]])
    else:
        print('could not setup connection')
        socket.close()

# client socket listener
def listen_to_client(user):
    while True:
        incomming = user.socket.recv()
        message = irc_message.from_string(incomming)
        dispatch_message(user, message)

def connect(message):
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
def dispatch_message(user, message):
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

    # handle each connection on a separate thread
    thread = Thread(target=new_connection, args=[client_socket])
    thread.start()

server_socket.close()
