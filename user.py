class User:
    def __init__(self, username, socket):
        self.name = username
        self.socket = socket
        self.rooms = []
