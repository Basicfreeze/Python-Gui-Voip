#!/usr/bin/env python
import pyaudio
import socket
from tinydb import TinyDB, Query
from threading import Thread
import sys
global clients
clients = []

# Pyaudio Initialization
chunk = 1024
pa = pyaudio.PyAudio()
addresses = {}
db = TinyDB('data/db.json')
user = Query()

# Opening of the audio stream
stream = pa.open(format = pyaudio.paInt16,
                channels = 1,
                rate = 10240,
                output = True,
                frames_per_buffer=chunk)

# Socket Initialization
host = 'localhost'
port = 50000
backlog = 5
size = 4096
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host,port))
sock.listen(backlog)
print "Server is now running\n======================="


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = sock.accept()
        print("%s:%s has connected." % client_address)
        addresses[client] = client_address
        clients.append(client)
        print 'first: '+str(client)
        Thread(target=analyze_data, args=(client,)).start()


def analyze_data(client):
    while True:
        try:
            data = client.recv(size)
            print data
            if data[0] == "1":
                answer = register_handler(credentials_clipper(data[1:]))
                client.send(answer)
            if data[0] == "2":
                answer = validator(credentials_clipper(data[1:]))
                client.send(answer)
            if data:
                broadcast(data, client)

        except socket.error:  # Possibly client has left the chat
            pass


def validator(data):
    username = str(data[0])
    password = str(data[1])
    print 'username: '+username
    print 'password: '+password
    print 'len1: '+str(len(db.search(user.name == username)))
    print 'len2: '+str(len(db.search(user.password == password)))
    if len(db.search(user.name == username)) == len(db.search(user.password == password)):
        print 'true'
        return "1"
    else:
        return "2"


def credentials_clipper(data):
    l = data.split(",")
    c = 0
    for item in l:
        item = item.replace("(", " ")
        item = item.replace(")", " ")
        item = item.replace("'", " ")
        item = item.strip(" ")
        l[c] = item
        c += 1
    return l

def broadcast(data, client):
    for person in clients:
        if person != client:
            stream.write(data)
            person.send("ACK")


def register_handler(data):
    print "username: "+str(data[0])
    print "password: " + str(data[1])
    if len(db.search(user.name == data[0])) == 1:
        return "2"
    else:
        db.insert({'name': data[0], 'password': data[1]})
        return "1"


print("Waiting for connection...")
ACCEPT_THREAD = Thread(target=accept_incoming_connections)
ACCEPT_THREAD.start()
ACCEPT_THREAD.join()
stream.close()
sock.close()
print "Server has stopped running"