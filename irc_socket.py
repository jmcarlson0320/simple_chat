from socket import *
from common import *

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
        # count bytes sent to make sure we send all of the message
        # could take multiple calls to send()
        total_sent = 0
        while total_sent < len(msg):
            num_bytes = self.socket.send(msg[total_sent:].encode())
            if num_bytes == 0:
                print('could not send')
            total_sent += num_bytes

    def recv(self, end_marker):
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
                print('could not receive')

            # find the end-of-message marker
            index_of_EOM = chunk.find(end_marker)
            # if end found
            if index_of_EOM != -1:
                # get rest of transmission
                chunks.append(chunk[:index_of_EOM])
                # check if we grabbed the beginning of next transmission also
                if len(chunk[:index_of_EOM]) > len(end_marker):
                    # set aside the beginning of the next transmission
                    self.start_of_next_transmission = chunk[(index_of_EOM + len(end_marker)):]
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
