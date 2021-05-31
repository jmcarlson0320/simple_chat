from irc_socket import *
from threading import Thread
from threading import Lock
from common import *
from irc_message import *
from user import *

PORT = 6000
ADDRESS = '0.0.0.0'

users_lock = Lock()
users = {}

rooms_lock = Lock()
rooms = {
    'room1': set(),
    'mathchat': set(),
    'sexytimeverniiicehowmuch': set()
}

def listen_to_client(user):
    while True:
        incomming = user.socket.recv()
        if not incomming:
            user.socket.close()

            users_lock.acquire()
            users.pop(user.name)
            users_lock.release()

            print('connection to ' + user.name + ' closed')
            return
        message = irc_message.from_string(incomming)
        handle_message(user, message)

def new_connection(socket):
    incomming = socket.recv()
    message = irc_message.from_string(incomming)
    op = message.operation
    argv = message.argv
    argc = message.argc
    if message.operation == CONNECT and message.argc == 1:
        new_user = User(message.argv[0], socket)

        users_lock.acquire()
        users[new_user.name] = new_user
        users_lock.release()

        print('new user')
        print('username: ' + message.argv[0])
        listen_to_client(new_user)
    else:
        print('could not setup user, closing connection')
        response = irc_message(ERROR, args=None, body='ERROR could not setup connection with server')
        socket.send(response.to_string())
        socket.close()

def list_rooms(user):
    header = ROOM_LIST
    room_names = rooms.keys()
    body = '\n'.join(room_names)
    msg = header + '\n' + body
    user.socket.send(msg)

def join_room(user, message):
    if message.argc != 1:
        return
    roomid = message.argv[0]
    if roomid not in rooms:
        rooms[roomid] = set()
        rooms[roomid].add(user)
    else:
        rooms[roomid].add(user)

def leave_room(message):
    pass

def list_users(messages):
    pass

def client_send_message(message):
    pass

# unpack and check errors here!
# if errors, dispatch to error handlers
def handle_message(user, message):
    op = message.operation
    if op == LIST_ROOMS:
        list_rooms(user)
    elif op == JOIN_ROOM:
        join_room(user, message)
    elif op == LEAVE_ROOM:
        leave_room(message)
    elif op == LIST_USERS:
        list_users(message)
    elif op == CLIENT_SEND_MESSAGE:
        client_send_message(message)
    else:
        print('unknown message from client')

def main():
    # setup listening socket
    server_socket = MyIRCSocket()
    server_socket.bind(ADDRESS, PORT)
    server_socket.listen()

    print('listening on port: ' + str(PORT))

    # accept new connections
    while True:
        (client_socket, client_address) = server_socket.accept()
        print('new connection from: ' + str(client_address))

        # handle each connection on a separate thread
        thread = Thread(target=new_connection, args=[client_socket])
        thread.start()

    server_socket.close()

if __name__ == '__main__':
    main()
