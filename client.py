import socket
import threading
import tkinter as tk
import tkinter.scrolledtext
from tkinter import simpledialog

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090
SIZE = 1024
FORMAT = 'utf-8'

class Client:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.connected = True

        print(f"[CONNECTED] Client connected to server at {host}:{port}")

        name_request = tk.Tk()  
        name_request.withdraw()              
        self.name = simpledialog.askstring("Name", "Enter your name.", parent=name_request)
        
        self.guiRendered = False
        gui_thread = threading.Thread(target=self.gui_render)
        gui_thread.start()

        fetch_thread = threading.Thread(target=self.fetch)
        fetch_thread.start()


    def gui_render(self):
        self.window = tk.Tk()
        self.window.configure(bg='lavender')

        self.title_frame = tk.Frame(self.window)
        self.title_frame.configure(bg='lavender')
        self.title_frame.pack(fill='x', padx=10, pady=10)

        self.window_label = tk.Label(self.title_frame, text=f"{self.name}", bg='lavender')
        self.window_label.config(font=('Arial', 12))
        self.window_label.pack(side=tk.LEFT, fill='x')

        self.quit_button = tk.Button(self.title_frame, text="QUIT", command=self.shutdown)
        self.quit_button.config(font=('Arial', 12))
        self.quit_button.pack(side=tk.RIGHT, fill='x')

        self.read_area = tk.scrolledtext.ScrolledText(self.window)
        self.read_area.pack(padx=10, pady=10)
        self.read_area.config(state='disabled')

        self.chat_frame = tk.Frame(self.window)
        self.chat_frame.configure(bg='lavender')
        self.chat_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        self.write_label = tk.Label(self.chat_frame, text="Your message", bg='lavender')
        self.write_label.config(font=('Arial', 12))
        self.write_label.pack(padx=10, pady=10)
        self.write_area = tk.Text(self.chat_frame, height=5)
        self.write_area.pack(side=tk.LEFT, padx=10, pady=10)

        self.send_button = tk.Button(self.chat_frame, text="SEND", command=self.write)
        self.send_button.config(font=('Arial', 12))
        self.send_button.pack(side=tk.RIGHT)

        self.guiRendered = True                                
        self.window.protocol('WM_DELETE_WINDOW', self.shutdown)    
        self.window.mainloop()                                 

    def write(self):
        message = self.write_area.get('1.0', 'end')
        self.client_socket.send(message.encode(FORMAT))
        self.write_area.delete('1.0', 'end')


    def shutdown(self):
        self.client_socket.send(f"Goodbye. <{self.name} has left the chat...>\n".encode(FORMAT))
        self.connected = False
        self.window.destroy()
        self.client_socket.close()
        exit(0)

    def fetch(self):
        while self.connected:
            try:
                message = self.client_socket.recv(SIZE).decode(FORMAT)
                
                if message == 'NAME_PROMPT':
                    self.client_socket.send(self.name.encode(FORMAT))

                else:
                    if self.guiRendered:
                        self.read_area.config(state='normal')
                        self.read_area.insert('end', message)
                        self.read_area.yview('end')
                        self.read_area.config(state='disabled')

            except ConnectionAbortedError:
                break

            except:
                print("Connection Error")
                self.client_socket.close()
                break

client = Client(HOST, PORT)