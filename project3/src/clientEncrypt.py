#!/usr/bin/env python3

import socket
import nacl.secret
import nacl.utils
from nacl.public import PrivateKey, Box
from nacl.encoding import Base64Encoder
import base64
import json

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server


class Chunks(object):
    """
    Data stucture that holds rolling checksums for file B
    """

    def __init__(self):
        self.chunks = []
        self.chunk_sigs = {}

    def append(self, sig):
        self.chunks.append(sig)
        # self.chunk_sigs.setdefault(sig.adler32, {})
        # self.chunk_sigs[sig.adler32][sig.md5] = len(self.chunks) - 1

    def get_chunk(self, chunk):
        adler32 = self.chunk_sigs.get(adler32_chunk(chunk))

        if adler32:
            return adler32.get(md5_chunk(chunk))

        return None

    def get_offset(self, md5):
        md5_offset = {sig.md5: sig.offset for sig in self.chunks}
        return md5_offset.get(md5)

    def copy(self):
        new_chunck = Chunks()
        for sigs in self.chunks:
            new_chunck.append(sigs)
        return new_chunck

    def __getitem__(self, idx):
        return self.chunks[idx]

    def __len__(self):
        pass


clientSecretKey = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # chunk.append(msg)

    # Receive Server's public key
    #pkServer = s.recv(1024)

    # Send client public k
    clientBox = nacl.secret.SecretBox(clientSecretKey)

    message = b'This is client message'
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    print(type(nonce))
    print('nonce ',nonce)
    print('nonce ',nonce.decode("utf-8", 'ignore'))
    # Encrypt Box
    encrypted = clientBox.encrypt(message, nonce)
    ctext = encrypted.ciphertext
    # Receiving the encryptedBox
    s.sendall(encrypted)

    box = s.recv(1024)

    serverBox = nacl.secret.SecretBox(clientSecretKey)
    print("Cipher Text is: ", ctext)
    serverMessage = serverBox.decrypt(box)
    serverMessage = serverMessage.decode('utf-8')
    print(serverMessage)

    # Send message
#     msg = {1:'hi', 2: 'there'}
#     str_json = json.dumps(msg)
#     s.sendall(str_json.encode())
#     data = s.recv(1024)
#     print('pkServer', pkServer)
#     print('skClient', skClient)
#     print('pkServer decoded', pkServer.decode())

#     print("eh")

#     client_box = Box(skClient, pkServer.decode())

#     data = client_box.decrypt(data)

# print(data.decode())
# print('Received', repr(data))
