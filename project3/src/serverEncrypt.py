#!/usr/bin/env python3
import socket
import nacl.utils
import json
from nacl.public import PrivateKey, Box
from nacl.encoding import Base64Encoder
import base64
import json
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            # Receiving client's public key
            data = conn.recv(1024)
            print("Received Box")
            conn.sendall(data)
            print("Sending Box back")

            if not data:
                break
#             print(data.decode())
#             conn.sendall(data)
