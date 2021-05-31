from irc_socket import *
from user_input import *
import sys
from threading import Thread
from threading import Lock
from common import *
from irc_message import *

'''
ERROR = 'ERROR'
ROOM_LIST = 'ROOM_LIST'
USER_LIST = 'USER_LIST'
SERVER_DISPATCH_MESSAGE = 'SERVER_DISPATCH_MESSAGE'
'''

PORT = 6000
ADDRESS = '127.0.0.1'

# signals client to shutdown
connection_open = False;

# setup client socket and connect to server
client_socket = MyIRCSocket()
client_socket.connect(ADDRESS, PORT)

connection_open = True

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
        dispatch_message(message)
        # dispatch message to handler

# listen on a thread so we can also accept user input
thread = Thread(target=listen_to_server, args=[client_socket])
thread.start()

def room_list(message):
    pass

def user_list(message):
    pass

def server_dispatch_message(message):
    pass

def error(message):
    print(message.body)

# unpack and check for errors here!
# dispatch to error handlers
def dispatch_message(message):
        op = message.operation
        if op == ROOM_LIST:
            room_list(message)
        elif op == USER_LIST:
            user_list(message)
        elif op == SERVER_DISPATCH_MESSAGE:
            server_dispatch_message(message)
        elif op == ERROR:
            error(message)
        else:
            print('unknown message from server')

''' user input code '''
def quit_program():
    pass

def send_join_msg():
    pass

def send_leave_msg():
    pass

def send_list_rooms_msg():
    pass

def send_list_users_msg():
    pass

def send_chat_message(msg):
    client_socket.send(msg)

def dispatch_command(command, argc, argv):
    if command == QUIT:
        quit_program()
    elif command == JOIN:
        send_join_msg()
    elif command == LEAVE:
        send_leave_msg()
    elif command == LIST_ROOMS:
        send_list_rooms_msg()
    elif command == LIST_USERS:
        send_list_users_msg()
    else:
        print('command not recognized')

''' main loop '''
while connection_open:
    text = input()
    user_input = input_fields(text)
    if user_input.cmd:
        dispatch_command(user_input.cmd, user_input.argc, user_input.argv)
    elif user_input.msg:
        send_chat_message(user_input.msg)

thread.join()
