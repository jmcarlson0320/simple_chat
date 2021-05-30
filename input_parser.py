from enum import Enum

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
