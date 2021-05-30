from socket import *
from enum import Enum

# end of message delimiter
EOM = '<END>'
CHUNK_SIZE = 1024

class MyIRCSocket:
    '''
    Wrapper for socket that sends/receives using an end of message delimiter.
    Sends/receives strings.
    '''
    def __init__(self, sock=None):
        if sock is None:
            self.socket = socket(AF_INET, SOCK_STREAM)
        else:
            self.socket = sock
        # holds start of next transmission in case we receive the end of one
        # message and the beginning of another in the same transmission
        self.start_of_next_transmission = ''

    def connect(self, host, port):
        self.socket.connect((host, port))

    def send(self, msg):
        # add end of message marker to end of message
        msg += EOM
        # count bytes sent to make sure we send all of the message
        # could take multiple calls to send()
        total_sent = 0
        while total_sent < len(msg):
            num_bytes = self.socket.send(msg[total_sent:].encode())
            if num_bytes == 0:
                raise RunTimeError('could not send')
            total_sent += num_bytes

    def recv(self):
        # buffer to hold pieces of message if it arrives in multiple
        # transmissions
        chunks = []

        # see if the start of a new message was already received
        if self.start_of_next_transmission:
            chunks.append(self.start_of_next_transmission)
            self.start_of_next_transmission = ''

        # call recv on the socket until we get all of the incomming message
        end_of_message = False
        while not end_of_message:
            chunk = self.socket.recv(CHUNK_SIZE).decode()
            if not chunk:
                raise RunTimeError('could not receive')

            # find the end-of-message marker
            index_of_EOM = chunk.find(EOM)
            # if end found
            if index_of_EOM != -1:
                # get rest of transmission
                chunks.append(chunk[:index_of_EOM])
                # check if we grabbed the beginning of next transmission also
                if len(chunk[:index_of_EOM]) > len(EOM):
                    # set aside the beginning of the next transmission
                    self.start_of_next_transmission = chunk[(index_of_EOM + len(EOM)):]
                end_of_message = True
            else:
                chunks.append(chunk[:index_of_EOM])
        # combine pieces of message into a single string
        return ''.join(chunks)

    def bind(self, address, port):
        self.socket.bind((address, port))

    def accept(self):
        socket, address = self.socket.accept()
        return (MyIRCSocket(socket), address)

    def listen(self):
        self.socket.listen()

    def close(self):
        self.socket.close()

''' input parsing '''

CMD_DELIMITER = ':'

class InputType(Enum):
    COMMAND = 0
    MESSAGE = 1
    NO_INPUT = 3

class CommandType(Enum):
    JOIN = 0
    LEAVE = 1
    LISTROOMS = 2
    LISTUSERS = 3
    QUIT = 4
    ERROR = 5

class InputParser:
    def __init__(self):
        self.input_type = None
        self.command = None
        self.args = []
        self.message_text = ''

    def parse_input(self, text):
        if not text:
            self.input_type = InputType.NO_INPUT
        if text[0] == CMD_DELIMITER:
            text = text[1:].split(' ')
            command_string = text[0]
            self.args = text[1:]
            if command_string == 'join' and len(self.args) == 1:
                self.command = CommandType.JOIN
            elif command_string == 'leave' and len(self.args) == 0:
                self.command = CommandType.LEAVE
            elif command_string == 'listrooms' and len(self.args) == 0:
                self.command = CommandType.LISTROOMS
            elif command_string == 'listusers' and len(self.args) == 0:
                self.command = CommandType.LISTUSERS
            elif command_string == 'quit' and len(self.args) == 0:
                self.command = CommandType.QUIT
            else:
                self.command = CommandType.ERROR
            self.input_type = InputType.COMMAND
        else:
            self.message_text = text
            self.input_type = InputType.MESSAGE
