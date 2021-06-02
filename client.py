from irc_socket import *
from user_input import *
import sys
from threading import Thread
from threading import Lock
from threading import Event
from common import *
from irc_message import *

PORT = 6000
ADDRESS = '127.0.0.1'

# setup client socket and connect to server
client_socket = MyIRCSocket()
client_socket.connect(ADDRESS, PORT)

# signals client to shutdown
connection_lock = Lock()
connection_open = True

def new_connection(socket):
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
            connection_open = False
            return
        message = irc_message.from_string(incomming)
        handle_message(message)
        # dispatch message to handler

# unpack and check for errors here!
# dispatch to error handlers
def handle_message(message):
    op = message.operation
    if op == ROOM_LIST:
        print_user_list(message.body)
    elif op == USER_LIST:
        print_user_list(message.body)
    elif op == SERVER_DISPATCH_MESSAGE:
        incomming_chat_message(message.argv[1], message.argv[0], message.body)
    elif op == ERROR:
        error(message)
    else:
        print('unknown message from server')

def print_room_list(rooms):
    if not rooms:
        print('[none]')
        return
    print(rooms)

def print_user_list(users):
    if not users:
        print('[none]')
        return
    print(users)

def incomming_chat_message(src, dest, body):
    print('[' + src + ']: ' + body)

def error(message):
    print(message.body)

''' handle user commands '''
def dispatch_command(command, argc, argv):
    if command == 'quit':
        quit_program()
    elif command == 'join':
        msg = JOIN_ROOM + ' ' + argv[0]
        client_socket.send(msg)
    elif command == 'leave':
        client_socket.send(LEAVE_ROOM)
    elif command == 'rooms':
        client_socket.send(LIST_ROOMS)
    elif command == 'users':
        client_socket.send(LIST_USERS)
    else:
        print('command not recognized')

# not sure how to do this one!!!
# threads make it complicated...
def quit_program():
    pass

def send_chat_msg(text):
    msg = irc_message(CLIENT_SEND_MESSAGE, body=text)
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
