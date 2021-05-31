from irc_socket import *
from input_parser import *
import sys
from threading import Thread
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

# setup client socket and connect to server
client_socket = MyIRCSocket()
client_socket.connect(ADDRESS, PORT)

# runs in a thread, handles incomming messages
def listen_to_server(socket):
    while True:
        incomming = socket.recv()
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
    pass

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
def handle_command(command, args):
    if command == CommandType.QUIT:
        sys.exit()
    elif command == CommandType.JOIN:
        client_socket.send(IRCCommand(command, args))
    else:
        print('command not recognized')

def send_message(msg):
    client_socket.send(msg)

parser = InputParser()

''' main loop '''
# wait for user input, process it as command or outgoing message
while True:
    from_console = input()
    parser.parse_input(from_console)
    if parser.input_type == InputType.COMMAND:
        handle_command(parser.command, parser.args)
    elif parser.input_type == InputType.MESSAGE:
        send_message(parser.message_text)
