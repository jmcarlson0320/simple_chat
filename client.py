from irc_socket import *
from user_input import *
import sys
from threading import Thread
from threading import Lock
from threading import Event
from common import *
from irc_message import *
import time

PORT = 6000
ADDRESS = '127.0.0.1'

# setup client socket and connect to server
client_socket = MyIRCSocket()
client_socket.connect(ADDRESS, PORT)

# client's username
username = ''

# signals client to shutdown
connection_lock = Lock()
connection_open = True

# room client is a member of
current_rooms_lock = Lock()
current_rooms = []

def new_connection(socket):
    global username
    username = input('enter a userid: ')
    while not username:
        username = input('enter a userid: ')
    msg = irc_message(CONNECT, args=[username])
    socket.send(msg.to_string())
    listen_to_server(socket)

# runs in a thread, handles incomming messages
def listen_to_server(socket):
    global connection_open
    while True:
        incomming = socket.recv()
        if not incomming:
            print('could not connect, press any key to exit...')
            socket.close()
            connection_lock.acquire()
            connection_open = False
            connection_lock.release()
            return
        message = irc_message.from_string(incomming)
        handle_message(message)
        # dispatch message to handler

# unpack and check for errors here!
# dispatch to error handlers
def handle_message(message):
    op = message.operation
    if op == ROOM_LIST:
        print_room_list(message.body)
    elif op == USER_LIST:
        print_user_list(message.body)
    elif op == SERVER_DISPATCH_MESSAGE:
        incomming_chat_message(message.argv[0], message.argv[1], message.body)
    elif op == ERROR:
        error(message)
    else:
        print('unknown message from server')

def print_room_list(roomlist):
    global current_rooms
    print('chatrooms: ', end='')
    if not roomlist:
        print('[no rooms]')
        return
    roomlist = roomlist.split(' ')
    for i in range(len(roomlist)):
        if roomlist[i] in current_rooms:
            roomlist[i] = '*' + roomlist[i]

    print(' '.join(roomlist))

def print_user_list(users):
    print('users in room: ', end='')
    if not users:
        print('[no users]')
        return
    print(users)

def time_stamp():
    t = time.localtime()
    clock_time = str(t.tm_hour) + ':' + str(t.tm_min)
    return clock_time

def incomming_chat_message(src, dest, body):
    print('[' + src + ']: ' + body)

def error(message):
    print(message.body)

''' handle user commands '''
def dispatch_command(command, argc, argv):
    global current_rooms
    print(current_rooms)
    if command == 'quit':
        quit_program()
    elif command == 'join':
        if argc != 1:
            print('must provide room id')
            return
        roomid = argv[0]
        send_join_request(roomid)
        add_to_current_rooms(roomid)
    elif command == 'leave':
        if argc != 1:
            print('must provide room id')
            return
        roomid = argv[0]
        send_leave_request(roomid)
        remove_from_current_rooms(roomid)
    elif command == 'rooms':
        request_room_list()
    elif command == 'users':
        if argc != 1:
            print('must provide room id')
            return
        roomid = argv[0]
        request_user_list(roomid)
    else:
        print('command not recognized')

# not sure how to do this one!!!
# threads make it complicated...
def quit_program():
    pass

def send_join_request(roomid):
    msg = irc_message(JOIN_ROOM, args=[roomid])
    client_socket.send(msg.to_string())

def add_to_current_rooms(roomid):
    current_rooms_lock.acquire()
    current_rooms.append(roomid)
    current_rooms_lock.release()

def send_leave_request(roomid):
    msg = irc_message(LEAVE_ROOM, args=[roomid])
    client_socket.send(msg.to_string())

def remove_from_current_rooms(roomid):
    if roomid not in current_rooms:
        return
    current_rooms_lock.acquire()
    current_rooms.remove(roomid)
    current_rooms_lock.release()

def request_room_list():
    msg = irc_message(LIST_ROOMS)
    client_socket.send(msg.to_string())

def request_user_list(roomid):
    msg = irc_message(LIST_USERS, args=[roomid])
    client_socket.send(msg.to_string())

def send_chat_msg(text, userid, roomid):
    msg = irc_message(CLIENT_SEND_MESSAGE, args=[userid, roomid], body=text)
    client_socket.send(msg.to_string())

def main():
    global connection_open

    # listen on a thread so we can also accept user input
    thread = Thread(target=new_connection, args=[client_socket])
    thread.start()

    while connection_open:
        text = input()
        user_input = input_fields(text)
        if user_input.cmd:
            dispatch_command(user_input.cmd, user_input.argc, user_input.argv)
        elif user_input.msg:
            send_chat_msg(user_input.msg)

    thread.join()

if __name__ == '__main__':
    main()
