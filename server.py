import socket
import threading
import tkinter
import tkinter.scrolledtext
import time
from tkinter import simpledialog

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090
ADDRESS = (HOST, PORT)
SIZE = 1024
FORMAT = 'utf-8'

class Server:
    def __init__(self, address):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = "Server"
        self.address = address
        self.clients = []
        self.connected = True

        self.window = tkinter.Tk()
        self.window.configure(bg='lavender')

        self.title_frame = tkinter.Frame(self.window)
        self.title_frame.configure(bg='lavender')
        self.title_frame.pack(fill='x', padx=10, pady=10)

        self.window_label = tkinter.Label(self.title_frame, text=f"{self.name}", bg='lavender')
        self.window_label.config(font=('Arial', 12))
        self.window_label.pack(side=tkinter.LEFT, fill='x')

        self.quit_button = tkinter.Button(self.title_frame, text="QUIT", command=self.shutdown)
        self.quit_button.config(font=('Arial', 12))
        self.quit_button.pack(side=tkinter.RIGHT, fill='x')

        self.read_area = tkinter.scrolledtext.ScrolledText(self.window)
        self.read_area.pack(padx=10, pady=10)
        self.read_area.config(state='disabled')

        self.chat_frame = tkinter.Frame(self.window)
        self.chat_frame.configure(bg='lavender')
        self.chat_frame.pack(side=tkinter.BOTTOM, padx=10, pady=10)

        self.write_label = tkinter.Label(self.chat_frame, text="Your message", bg='lavender')
        self.write_label.config(font=('Arial', 12))
        self.write_label.pack(padx=10, pady=10)
        self.write_area = tkinter.Text(self.chat_frame, height=5)
        self.write_area.pack(side=tkinter.LEFT, padx=10, pady=10)

        self.send_button = tkinter.Button(self.chat_frame, text="SEND", command=self.write)
        self.send_button.config(font=('Arial', 12))
        self.send_button.pack(side=tkinter.RIGHT)

    def start(self):
        self.server.bind(self.address)
        self.server.listen()
        print(f"Server is listening on {HOST}:{PORT}")

        accept_thread = threading.Thread(target=self.accept_client)
        accept_thread.start()

        self.window.protocol('WM_DELETE_WINDOW', self.shutdown) 
        self.window.mainloop()

    def broadcast(self, bubble):
        for client in self.clients:
            client.send(bubble)

    def shutdown(self):
        print(f"Server is shutting down...")
        self.connected = False
        self.window.destroy()
        self.server.close()
        exit(0)

    def write(self):
        message = self.write_area.get('1.0', 'end')
        bubble = f"{self.name}: {message}"
        print(bubble)

        self.read_area.config(state='normal')
        self.read_area.insert('end', bubble)
        self.read_area.yview('end')
        self.read_area.config(state='disabled')

        self.write_area.delete('1.0', 'end')
        self.broadcast(bubble.encode(FORMAT))


    def handle_client(self, client, name):
        while self.connected:
            try:
                message = client.recv(SIZE).decode(FORMAT)
                if message:
                    bubble = f"{name.decode(FORMAT)}: {message}"
                    print(bubble)
                    
                    self.read_area.config(state='normal')
                    self.read_area.insert('end', bubble)
                    self.read_area.yview('end')
                    self.read_area.config(state='disabled')

                    self.broadcast(bubble.encode(FORMAT))
            except:
                self.clients.remove(client)
                client.close()
                break


    def accept_client(self):
        while self.connected:
            try:
                client, address = self.server.accept()
                self.clients.append(client)
                print(f"Connected with {str(address)}")

                client.send("NAME_PROMPT".encode(FORMAT))
                name = client.recv(SIZE)

                self.read_area.config(state='normal')
                self.read_area.insert('end', f"[WELCOME] {name.decode(FORMAT)} joined the chat.\n".encode(FORMAT))
                self.read_area.yview('end')
                self.read_area.config(state='disabled')

                self.broadcast(f"[WELCOME] {name.decode(FORMAT)} joined the chat.\n".encode(FORMAT))
                time.sleep(1)
                client.send(f"{self.name}: Greetings {name.decode(FORMAT)}!\n".encode(FORMAT))

                client_thread = threading.Thread(target=self.handle_client, args=(client, name))
                client_thread.start()

            except:
                if self.connected:
                    print(f"Connection error.")


server = Server(ADDRESS)
server.start()