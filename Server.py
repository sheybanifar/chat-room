import threading
import socket as s

# initializing server socket. 
while True:
    try:
        host = input("Enter interface address as IPv4 (example: 127.0.0.1): ")
        if host:
            PORT = 2001
            ADDRESS = (host, PORT)
            server = s.socket(s.AF_INET, s.SOCK_STREAM)
            try:
                server.bind(ADDRESS)
            except s.gaierror:
                print('incorrect server address!')
                continue
            server.listen()
            break
        else:
            continue
    except EOFError:
        print('invalid input!')
        continue

# these lists are used for saving client's sockets & their aliases.
clients = []
aliases = []

# "event" is intended to kill alive threads (stop busy waiting tasks)
# while facing server crash or Keyboard interruption. but, it seems
# useless idea!!! so I appreciate you to guide me about managing threads
# life-cycle.
event = threading.Event()

def broadcast(message, passed_client):
    for client in clients:
        if client is passed_client:
            continue
        client.send(message)

def handle_client(client):
    while True:
        try:
            if event.is_set():
                index = clients.index(client)
                clients.remove(client)
                client.shutdown(s.SHUT_RDWR)
                client.close()
                aliases.remove(aliases[index])
                break
            message = client.recv(1024)
            broadcast(message, client)
        except:
            event.set()
            index = clients.index(client)
            clients.remove(client)
            client.shutdown(s.SHUT_RDWR)
            client.close()
            broadcast(f'\n{aliases[index]} has left the chat room!'.encode(), client)
            aliases.remove(aliases[index])
            break

def receive():
    while True:
        try:
            # !!!!! must change to listening to {IP ADDRESS}
            print(f'"{host}" Listening...')
            client, address = server.accept()
            client.send('alias?'.encode())
            alias = client.recv(1024).decode()
        except KeyboardInterrupt:
            print('you pressed "Control + C", so Server disconnected!')
            event.set()
            break
        except:
            print('Some thing went wrong!')
            event.set()
            client.shutdown(s.SHUT_RDWR)
            client.close()
            break
        print(f'{alias} connected successfully.', address)
        broadcast(f'\n{alias} was joined the room.'.encode(), client)
        client.send('you\'re welcome!\n'.encode())
        clients.append(client)
        aliases.append(alias)
        # Every accepted connection will has a thread to interact with
        # its client.
        client_thread = threading.Thread(
            target=handle_client,
            args=(client,),
            name='T-'+ alias
        )
        client_thread.start()

if __name__ == '__main__':
    receive()