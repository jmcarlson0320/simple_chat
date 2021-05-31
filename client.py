from irc_socket import *
from user_input import *
import sys
from threading import Thread
from threading import Lock
from common import *
from irc_message import *

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
    print(message.body)

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

''' handle user commands '''
def quit_program():
    pass

def dispatch_command(command, argc, argv):
    if command == 'quit':
        quit_program()
    elif command == 'join':
        msg = JOIN_ROOM + ' ' + argv[0]
        client_socket.send(msg)
    elif command == 'leave':
        pass
    elif command == 'listrooms':
        client_socket.send(LIST_ROOMS)
    elif command == 'listusers':
        pass
    else:
        print('command not recognized')

''' main loop '''
while connection_open:
    text = input()
    user_input = input_fields(text)
    if user_input.cmd:
        dispatch_command(user_input.cmd, user_input.argc, user_input.argv)
    elif user_input.msg:
        client_socket.send(user_input.msg)

thread.join()
