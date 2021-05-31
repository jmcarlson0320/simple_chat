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
        op = message.operation
        if op == ROOM_LIST:
            # print room list
            print(message.body)
        elif op == USER_LIST:
            # print user list
            print(message.body)
        elif op == SERVER_DISPATCH_MESSAGE:
            # print incomming chat message
            print(message.body)
        elif op == ERROR:
            # handle error
            print('server sent client an error: ' + message.body)
        else:
            # uh oh, we don't recognize the message header...
            print('unknown message from server')

# listen on a thread so we can also accept user input
thread = Thread(target=listen_to_server, args=[client_socket])
thread.start()

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

# wait for user input, process it as command or outgoing message
while True:
    from_console = input()
    parser.parse_input(from_console)
    if parser.input_type == InputType.COMMAND:
        handle_command(parser.command, parser.args)
    elif parser.input_type == InputType.MESSAGE:
        send_message(parser.message_text)
