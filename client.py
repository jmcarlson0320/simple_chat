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

chat_target = None

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
            print('lost connection with server, press any key to exit...')
            socket.close()
            connection_lock.acquire()
            connection_open = False
            connection_lock.release()
            return
        message = irc_message.from_string(incomming)
        handle_message(message)
        # dispatch message to handler

def handle_message(message):
    op = message.operation
    if op == ROOM_LIST:
        print_room_list(message.body)
    elif op == USER_LIST:
        print_user_list(message.argv[0], message.body)
    elif op == SERVER_DISPATCH_MESSAGE:
        incomming_chat_message(message.argv[0], message.argv[1], message.body)
    elif op == ERROR:
        error(message)
    else:
        print('unknown message from server')

def print_room_list(roomlist):
    global current_rooms
    global chat_target
    print('[chatrooms]: ', end='')
    if not roomlist:
        print('[no rooms]')
        return
    roomlist = roomlist.split(' ')
    for i in range(len(roomlist)):
        if roomlist[i] == chat_target:
            roomlist[i] = '>>' + roomlist[i] + '*'
        elif roomlist[i] in current_rooms:
            roomlist[i] = roomlist[i] + '*'

    print(' '.join(roomlist))

def print_user_list(roomid, users):
    print('[' + roomid + ']: ', end='')
    if not users:
        print('[no users]')
        return
    userlist = users.split(' ')
    for i in range(len(userlist)):
        userlist[i] = "'" + userlist[i] + "'"
    print(' '.join(userlist))

def time_stamp():
    t = time.localtime()
    clock_time = str(t.tm_hour) + ':' + str(t.tm_min)
    return clock_time

def incomming_chat_message(src, dest, body):
    if body:
        dest = '[' + dest + ']'
        src = '<' + src + '>'
        out = '[{0:s}]{1:s} {2:s} {3:s}'.format(time_stamp(), dest, src, body)
        print(out)

def error(message):
    print(message.body)

''' handle user commands '''
def dispatch_command(command, argc, argv):
    global connection_open
    global current_rooms
    global chat_target
    if command == 'quit':
        quit_program()
        connection_open = False
    elif command == 'join':
        if argc != 1:
            print('must provide room id')
            return
        roomid = argv[0]
        send_join_request(roomid)
        add_to_current_rooms(roomid)
        chat_target = roomid
    elif command == 'leave':
        if argc != 1:
            print('must provide room id')
            return
        roomid = argv[0]
        send_leave_request(roomid)
        remove_from_current_rooms(roomid)
        if chat_target == roomid:
            chat_target = None
    elif command == 'rooms':
        request_room_list()
    elif command == 'users':
        if argc != 1:
            print('must provide room id')
            return
        roomid = argv[0]
        request_user_list(roomid)
    elif command == 'to':
        if argc < 1:
            print('must provide a room id')
            return
        roomid = argv[0]
        if roomid in current_rooms:
            chat_target = roomid
        else:
            print('must be a member of target room')
    else:
        print('command not recognized')

# not sure how to do this one!!!
# threads make it complicated...
def quit_program():
    print('\nexiting...')
    if client_socket:
        client_socket.close()

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
    global username
    global chat_target

    username = input('enter a userid: ')
    while not username:
        username = input('enter a userid: ')
    msg = irc_message(CONNECT, args=[username])
    client_socket.send(msg.to_string())

    # listen on a thread so we can also accept user input
    thread = Thread(target=listen_to_server, args=[client_socket])
    thread.daemon = True
    thread.start()

    while connection_open:
        text = input()

        user_input = input_fields(text)
        if user_input.cmd:
            dispatch_command(user_input.cmd, user_input.argc, user_input.argv)
        else:
            if chat_target and user_input.msg:
                send_chat_msg(user_input.msg, username, chat_target)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        quit_program()
