CMD_DELIMITER = ':'
# user commands
QUIT = 'quit'
JOIN = 'join'
LEAVE = 'leave'
LIST_ROOMS = 'listrooms'
LIST_USERS = 'listusers'

class input_fields:
    def __init__(self, text):
        self.cmd = None
        self.argv = None
        self.argc = 0
        self.msg = None

        if not text:
            return None

        if text[0] == CMD_DELIMITER:
            text_fields = text.split(' ')
            self.cmd = text_fields[0]
            if len(text_fields) > 1:
                self.argv = text_fields[1:]
                self.argc = len(self.argv)
            else:
                self.argv = None
                self.argc = 0
            self.msg = None
        else:
            self.cmd = None
            self.argv = None
            self.argc = 0
            self.msg = text
