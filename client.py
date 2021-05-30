from socket import *
from threading import Thread
from common import *

PORT = 6000
ADDRESS = '127.0.0.1'

# setup client socket and connect to server
client_socket = MyIRCSocket()
client_socket.connect(ADDRESS, PORT)

# runs in a thread, handles incomming messages
def listen_to_server(socket):
    while True:
        message = socket.recv()
        print(message)

# listen on a thread so we can also accept user input
thread = Thread(target=listen_to_server, args=[client_socket])
thread.start()

def handle_command(command, args):
    if command == CommandType.QUIT:
        quit()

def handle_message(msg):
    client_socket.send(from_console)

parser = InputParser()

# wait for user input, send it as a message to the server
while True:
    from_console = input()
    parser.parse_input(from_console)
    if parser.input_type == InputType.COMMAND:
        handle_command(parser.command, parser.args)
    elif parser.input_type == InputType.MESSAGE:
        handle_message(parser.message_text)
