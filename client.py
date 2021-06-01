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
connection_lock = Lock()
connection_open = False;

def new_connection(socket):
    username = input('enter a userid: ')
    msg = CONNECT + ' ' + username
    socket.send(msg)
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
        room_list(message)
    elif op == USER_LIST:
        user_list(message)
    elif op == SERVER_DISPATCH_MESSAGE:
        server_dispatch_message(message)
    elif op == ERROR:
        error(message)
    else:
        print('unknown message from server')

def room_list(message):
    print(message.body)

def user_list(message):
    pass

def server_dispatch_message(message):
    print(message.body)

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
        pass
    elif command == 'listrooms':
        client_socket.send(LIST_ROOMS)
    elif command == 'listusers':
        pass
    else:
        print('command not recognized')

def quit_program():
    pass

def join():
    pass

def leave():
    pass

def listrooms():
    pass

def listusers():
    pass

def send_chat_msg(text):
    header = CLIENT_SEND_MESSAGE
    body = text
    msg = header + '\n' + body
    client_socket.send(msg)

def main():
    global connection_open

    # setup client socket and connect to server
    client_socket = MyIRCSocket()
    client_socket.connect(ADDRESS, PORT)

    connection_open = True

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
