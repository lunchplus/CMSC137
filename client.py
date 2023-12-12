import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

HOST = '127.0.0.1'
PORT = 9090

class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port)) # connect to a server

        popup = tkinter.Tk()  
        popup.withdraw()              # run nickname popup in background

        # popup to get nickname
        self.nickname = simpledialog.askstring("Nickname", "Please type your nickname.", parent=popup)
        
        # start GUI setup flag
        self.gui_done = False

        # start GUI process flag
        self.running = True

        # create threads for GUI window and message receive process
        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)
        gui_thread.start()
        receive_thread.start()


    def gui_loop(self):
        # chat GUI window
        self.win = tkinter.Tk()

        # decorate window
        self.win.configure(bg='lavender')
        self.chat_label = tkinter.Label(self.win, text=f"{self.nickname} Chatbox", bg='lavender')
        self.chat_label.config(font=('Arial', 12))
        self.chat_label.pack(padx=20, pady=10)

        # decorate broadcast area
        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=10)
        self.text_area.config(state='disabled')

        # decorate input area
        self.msg_label = tkinter.Label(self.win, text="Your message", bg='lavender')
        self.msg_label.config(font=('Arial', 12))
        self.msg_label.pack(padx=20, pady=10)
        self.input_area = tkinter.Text(self.win, height=5)
        self.input_area.pack(padx=20, pady=10)

        # decorate button
        self.send_button = tkinter.Button(self.win, text="SEND", command=self.write)
        self.send_button.config(font=('Arial', 12))
        self.send_button.pack(padx=20, pady=10)

        self.gui_done = True                                # finished decorating
        self.win.protocol('WM_DELETE_WINDOW', self.stop)    # properly stop if window is closed
        self.win.mainloop()                                 # last line of execution loop

    # send user input in input area, and then clear once sent
    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    # proper steps to close connection if window is closed
    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    # 
    def receive(self):
        while self.running:
            try:

                # listen for message from server
                message = self.sock.recv(1024).decode('utf-8')

                # send nickname
                if message == 'GET_NICKNAME':
                    self.sock.send(self.nickname.encode('utf-8'))

                else:
                    # temporarily enable broadcast area to insert message
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')

            except ConnectionAbortedError:
                break

            except:
                print("Error")
                self.sock.close()
                break

# create an instance connected to host IP and port
client = Client(HOST, PORT)





        