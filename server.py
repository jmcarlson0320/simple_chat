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
    if incomming == 0:
        print('connection closed immediately')
        socket.close()
        return
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
        send_roomlist(new_user.socket)
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

            rooms_lock.acquire()
            for room in user.rooms:
                rooms[room].remove(user)
            rooms_lock.release()

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
        send_roomlist(user.socket)
    elif op == JOIN_ROOM:
        roomid = message.argv[0]
        add_user_to_room(user, roomid)
        for users in rooms[roomid]:
            send_userlist(users.socket, roomid)
    elif op == LEAVE_ROOM:
        roomid = message.argv[0]
        if remove_user_from_room(user, roomid):
            for users in rooms[roomid]:
                send_userlist(users.socket, roomid)
    elif op == LIST_USERS:
        roomid = message.argv[0]
        send_userlist(user.socket, roomid)
    elif op == CLIENT_SEND_MESSAGE:
        src = message.argv[0]
        dest = message.argv[1]
        dispatch_message_to_room(message.body, user, dest)
    else:
        print('unknown message from client: ' + message.to_string())
        # on error, close connection to client

def send_roomlist(socket):
    msg = irc_message(ROOM_LIST, body=' '.join(rooms.keys()))
    socket.send(msg.to_string())

def add_user_to_room(user, roomid):
    # if already a member, return
    if roomid in user.rooms:
        return

    rooms_lock.acquire()
    # if new room
    if roomid not in rooms:
        rooms[roomid] = set()
    rooms[roomid].add(user)
    rooms_lock.release()

    user.rooms.append(roomid)

def remove_user_from_room(user, roomid):
    if roomid not in user.rooms:
        return False

    rooms_lock.acquire()
    rooms[roomid].remove(user)
    rooms_lock.release()
    user.rooms.remove(roomid)
    return True

def send_userlist(socket, roomid):
    if roomid not in rooms.keys():
        return
    userids = []
    for users in rooms[roomid]:
        userids.append(users.name)
    msg = irc_message(USER_LIST, args=[roomid], body=' '.join(userids))
    socket.send(msg.to_string())

def dispatch_message_to_room(text, user, roomid):
    if roomid not in user.rooms:
        return 
    src = user.name
    dest = roomid
    msg = irc_message(SERVER_DISPATCH_MESSAGE, [src, dest], text)
    for dest_user in rooms[roomid]:
        if user.name != dest_user.name:
            dest_user.socket.send(msg.to_string())

def log_message(message):
    time_stamp = time.ctime(time.time())
    print('[' + time_stamp + ']\n' + message.to_string())

def main():
    # setup listening socket
    server_socket = MyIRCSocket()
    server_socket.bind(ADDRESS, PORT)
    server_socket.listen()

    client_threads = []

    print('listening on port: ' + str(PORT))

    # accept new connections
    while True:
        (client_socket, client_address) = server_socket.accept()
        print('new connection from: ' + str(client_address))

        # handle each connection on a separate thread
        thread = Thread(target=new_connection, args=[client_socket])
        thread.daemon = True
        thread.start()
        client_threads.append(thread)

    server_socket.close()

if __name__ == '__main__':
    main()
