import pyaudio
import socket
import sys
import time
import threading
import Tkinter as tk
import pickle

# Pyaudio Initialization
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 10240
LARGE_FONT = ("Calibri", 12)


p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=chunk)

# Socket Initialization
host = 'localhost'
port = 50000
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))


class Father(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        container.pack(side="top", anchor="center", expand="true")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        self.frames = {}
        for F in (StartPage, RegFrame, RegFrame, VoipFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Button(self, text="Login", height="2", width="30", font=LARGE_FONT, command=lambda :controller.show_frame(RegFrame)).pack(anchor="center", side="top")
        tk.Label(self, text="").pack()
        tk.Button(self, text="Register", height="2", width="30", font=LARGE_FONT, command=lambda: controller.show_frame(RegFrame)).pack(anchor="center", side="top")


class RegFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        but1 = tk.Button(self, text="Go Back", command=lambda: self.controller.show_frame(StartPage))
        but1.pack(side="top", anchor="nw")
        info_label = tk.Label(self, text="Enter Information below")
        info_label.pack()
        user_label = tk.Label(self, text="Username (required)")
        user_label.pack()
        username_entry = tk.Entry(self, textvariable=self.username)
        username_entry.pack()
        tk.Label(self, text="").pack()
        pass_label = tk.Label(self, text="Password")
        pass_label.pack()
        password_entry = tk.Entry(self, textvariable=self.password)
        password_entry.pack()
        tk.Label(self, text="").pack()
        but2 = tk.Button(self, text="Register", height="1", width="10", command=self.start_register)
        but2.pack()

    def start_register(self):
        t = threading.Thread(target=self.register_user)
        t.start()
        self.receive()

    def register_user(self):
        username_info = self.username.get()
        password_info = self.password.get()
        data = username_info, password_info
        s.send("1"+str(data))

    def receive(self):
        text = s.recv(size)
        if "1" in text:
            lab = tk.Label(self, text="Successfully Registered")
            lab.pack(side="bottom", anchor="center")
        elif "2" in text:
            lab2 = tk.Label(self, text="Username already exsits!")
            lab2.pack(side="bottom", anchor="center")


class RegFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        but1 = tk.Button(self, text="Go Back", command=lambda: self.controller.show_frame(StartPage))
        but1.pack(side="top", anchor="center")
        info_label = tk.Label(self, text="Enter Information below")
        info_label.pack()
        user_label = tk.Label(self, text="Username")
        user_label.pack()
        username_entry = tk.Entry(self, textvariable=self.username)
        username_entry.pack()
        tk.Label(self, text="").pack()
        pass_label = tk.Label(self, text="Password")
        pass_label.pack()
        password_entry = tk.Entry(self, textvariable=self.password)
        password_entry.pack()
        tk.Label(self, text="").pack()
        but2 = tk.Button(self, text="Login", height="1", width="10", command=self.validate)
        but2.pack()

    def validate(self):
        username_info = self.username.get()
        password_info = self.password.get()
        data = username_info, password_info
        s.send("2"+str(data))
        text = s.recv(size)
        if "1" in text:
            lab = tk.Label(self, text="Logged in Successfully")
            lab.pack(side="bottom", anchor="center")
            button = tk.Button(self, text="go to chat", height="1", width="10", command=lambda: self.controller.show_frame(VoipFrame)).pack()
        elif "2" in text:
            lab2 = tk.Label(self, text="One of the credentials is wrong!")
            lab2.pack(side="bottom", anchor="center")


class VoipFrame(tk.Frame):

    def on_mouse_down(self, event):
        self.mute = False
        self.speak_start()

    def mute_speak(self, event):
        self.mute = True
        print "You are now muted"

    def speak_start(self):
        t = threading.Thread(target=self.speak)
        t.start()

    def speak(self):
        print "You are now speaking"
        while self.mute is False:
            data = stream.read(chunk)
            s.send(data)
            s.recv(size)

    def create_widgets(self):
        self.speakb = tk.Button(self)
        self.speakb["text"] = "Speak"
        self.speakb.pack(side="top", anchor="center")

        self.speakb.bind("<ButtonPress-1>", self.on_mouse_down)
        self.speakb.bind("<ButtonRelease-1>", self.mute_speak)

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.mute = True
        self.mouse_pressed = False
        self.pack()
        self.controller = controller
        self.create_widgets()


app = Father()
app.mainloop()
s.close()
stream.close()
p.terminate()