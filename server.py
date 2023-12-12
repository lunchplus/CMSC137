import socket
import threading

HOST = '127.0.0.1'
PORT = 9090

# create a server that is an INET, STREAMING socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind server to own address so clients can connect
server.bind((HOST, PORT))
server.listen()

# address book for client address and their nicknames
clients = []
nicknames = []

# broadcast client messages to all clients
def broadcast(message):
    for client in clients:
        client.send(message)

# handle client messages and actions
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(message.decode('utf-8'))
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break


# receive connection request from a client while server is active
# create a thread for that client
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}!")

        client.send("GET_NICKNAME".encode('utf-8'))
        nickname = client.recv(1024)

        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of the client is {nickname.decode('utf-8')}")
        broadcast(f"{nickname.decode('utf-8')} joined the chat.\n".encode('utf-8'))
        client.send(f"Successfully connected to the server".encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is running...")
receive()
