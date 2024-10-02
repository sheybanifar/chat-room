import threading
import socket as s
from os import system

# Get appropriate alias from user
while True:
    try:
        alias = input('Enter your alias: ')
        if alias:
           break
        else:
            system('cls')
            continue
    except EOFError:
        system('cls')
        print('not accepted!')
        continue

# User must enter server address to connect
while True:
    try:
        host = input("Enter server address as IPv4 (example: 127.0.0.1): ")
        if host:
            PORT = 2001
            address = (host, PORT)
            client = s.socket(s.AF_INET, s.SOCK_STREAM)
            try:
                client.connect(address)
            except (TimeoutError, ConnectionRefusedError, s.gaierror):
                print('incorrect server address!')
                continue
            system('cls')
            break
        else:
            continue
    except EOFError:
        print('invalid input!')
        continue

try:
    server_question = client.recv(1024).decode()
except:
    print('Error! Disconnected.')
    client.shutdown(s.SHUT_RDWR)
    client.close()
    exit()
if server_question == 'alias?':
    client.send(alias.encode())

# "event" is intended to kill send & receive threads together immediately.
# but, it seems useless idea!!! it doesn't work as expected! 
# so I appreciate you to guide me about resolving this issue:
event = threading.Event()

# Busy waiting task for gathering user messages & sending
# to the other members.
def send():
    while True:
        if event.is_set():
            break
        try:
            user_input = input(f'{alias}: ')
            if user_input:
                message = f'\n{alias}: {user_input}'
                client.send(message.encode())
        except (EOFError, OSError):
            print('\nexiting the room...')
            event.set()
            break
# Busy waiting task for receiving members messages
# and printing them to the user.
def receive():
    while True:
        if event.is_set():
            break
        try:
            message = client.recv(1024).decode()
            if message:
                print(message, end='')
        except:
            print('\nyou\'re disconnected!')
            event.set()
            client.shutdown(s.SHUT_RDWR)
            client.close()
            break

# Here two thread are created & "receive" and "send"
# functions will pass to to them as target.
recveive_thread = threading.Thread(
    target=receive,
    name='T-receive'
)

recveive_thread.start()

send_thread = threading.Thread(
    target=send,
    name='T-send'
)

send_thread.start()
