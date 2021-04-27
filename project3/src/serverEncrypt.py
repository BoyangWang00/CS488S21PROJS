#!/usr/bin/env python3
import socket
import nacl.utils
import json
from nacl.public import PrivateKey, Box, PublicKey
from nacl.encoding import Base64Encoder
import json
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

skServer = PrivateKey.generate()
pkServer = skServer.public_key

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            #Send Server's public key
            print(type(pkServer)) #type nacl.public.PublicKey
            print('pkServer', pkServer)
            conn.sendall(pkServer.encode(Base64Encoder))
            #pkey_json = json.dumps(pkServer)
            #encoded_public_key = pkServer.public_key.encode(encoder=nacl.encoding.Base64Encoder)
            #conn.sendall(encoded_public_key)

            pkClient = conn.recv(1024) 
            print('pkServer encoded', pkClient.decode())
            data = conn.recv(1024)
            if not data:
                break
            print(data.decode())
            conn.sendall(data)

server_box = Box(skServer, pkClient)