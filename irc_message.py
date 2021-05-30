from enum import Enum

# message operation codes
ERROR = 'ERROR'
CONNECT = 'CONNECT'
LIST_ROOMS = 'LIST_ROOMS'
JOIN_ROOM = 'JOIN_ROOM'
LEAVE_ROOM = 'LEAVE_ROOM'
LIST_USERS = 'LIST_USERS'
CLIENT_SEND_MESSAGE = 'CLIENT_SEND_MESSAGE'
ROOM_LIST = 'ROOM_LIST'
USER_LIST = 'USER_LIST'
SERVER_DISPATCH_MESSAGE = 'SERVER_DISPATCH_MESSAGE'
KEEP_ALIVE = 'KEEP_ALIVE'

# error types:
ERROR_UNSPECIFIED = 'ERROR_UNSPECIFIED'
ERROR_TIMEOUT = 'ERROR_TIMEOUT'


class irc_message:
    def __init__(self, operation, args=None, body=None):
        self.operation = operation
        self.args = args
        self.body = body

    @classmethod
    def from_string(cls, text):
        text_lines = text.split('\n')
        header = text_lines[0]
        header_fields = header.split(' ')

        # get operation
        operation = header_fields[0]

        # get args
        if len(header_fields) > 1:
            args = header_fields[1:]
        else:
            args = None

        # get body
        if len(text_lines) > 1:
            body = '\n'.join(text_lines[1:])
        else:
            body = None

        # construct message object
        return cls(operation, args, body)

    def to_string(self):
        # build message
        # return as string
        pass
