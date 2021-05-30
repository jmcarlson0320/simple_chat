from irc_message import *

msg = '''CONNECT username1234
this is the message body
some more
'''

a = irc_message(LIST_ROOMS, ['arg1', 'arg2', 'secret fucking arg'], 'some body text...')
print(a.operation)
print(a.args)
print(a.body)
b = irc_message.from_string(msg)
print(b.operation)
print(b.args)
print(b.body)
