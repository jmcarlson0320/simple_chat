from irc_socket import *
from threading import Thread
from threading import Lock
from threading import Event
from common import *
from irc_message import *
from user import *
import time

PORT = 6000
ADDRESS = '0.0.0.0'

users_lock = Lock()
users = {}

rooms_lock = Lock()
rooms = {}

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
        list_rooms(new_user)
        listen_to_client(new_user)
    else:
        print('could not setup user, closing connection')
        response = irc_message(ERROR, args=None, body='ERROR could not setup connection with server')
        socket.send(response.to_string())
        socket.close()

def listen_to_client(user):
    while True:
        incomming = user.socket.recv()
        if not incomming:
            user.socket.close()

            users_lock.acquire()
            users.pop(user.name)
            users_lock.release()

            if user.room:
                rooms_lock.acquire()
                rooms[user.room].remove(user)
                rooms_lock.release()

            user.room = None

            print('connection to ' + user.name + ' closed')
            return
        message = irc_message.from_string(incomming)
        handle_message(user, message)

# unpack and check errors here!
# if errors, dispatch to error handlers
def handle_message(user, message):
    log_message(message)
    op = message.operation
    if op == LIST_ROOMS:
        list_rooms(user)
    elif op == JOIN_ROOM:
        join_room(user, message)
    elif op == LEAVE_ROOM:
        leave_room(user)
    elif op == LIST_USERS:
        list_users(user)
    elif op == CLIENT_SEND_MESSAGE:
        client_send_message(user, message)
    else:
        print('unknown message from client: ' + message.to_string())
        # on error, close connection to client

def list_rooms(user):
    msg = irc_message(ROOM_LIST, body=' '.join(rooms.keys()))
    user.socket.send(msg.to_string())

def join_room(user, message):
    if message.argc != 1:
        return
    if user.room:
        rooms_lock.acquire()
        rooms[user.room].remove(user)
        rooms_lock.release()
    roomid = message.argv[0]
    if roomid not in rooms:
        rooms_lock.acquire()
        rooms[roomid] = set()
        rooms_lock.release()
    rooms_lock.acquire()
    rooms[roomid].add(user)
    rooms_lock.release()
    user.room = roomid
    for users in rooms[roomid]:
        list_users(users)

def leave_room(user):
    if not user.room:
        return
    rooms_lock.acquire()
    rooms[user.room].remove(user)
    rooms_lock.release()
    for users in rooms[user.room]:
        list_users(users)
    user.room = None

def list_users(user):
    if not user.room:
        return
    usernames = []
    for users in rooms[user.room]:
        usernames.append(users.name)
    msg = irc_message(USER_LIST, body=' '.join(usernames))
    user.socket.send(msg.to_string())

def client_send_message(user, message):
    if not user.room:
        return 
    dest = user.room
    src = user.name
    msg = irc_message(SERVER_DISPATCH_MESSAGE, [dest, src], message.body)
    print(msg.to_string())
    for users in rooms[user.room]:
        if users.name != user.name:
            users.socket.send(msg.to_string())

def log_message(message):
    time_stamp = time.ctime(time.time())
    print('[' + time_stamp + ']\n' + message.to_string())

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
