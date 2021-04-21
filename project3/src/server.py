import collections
import hashlib
import zlib
import socket
import sys
import json

#Server has new file α
BLOCK_SIZE = 4

# Hasher
# Helper functions
# ----------------


def md5_chunk(chunk):
    """
    Returns md5 checksum for chunk
    """
    m = hashlib.md5()
    m.update(chunk)
    return m.hexdigest()


def adler32_chunk(chunk):
    """
    Returns adler32 checksum for chunk
    """
    return zlib.adler32(chunk)


# Checksum objects
# ----------------
Signature = collections.namedtuple('Signature', 'md5 adler32')


class Chunks(object):
    """
    Data stucture that holds rolling checksums for file B
    """

    def __init__(self):
        self.chunks = []
        self.chunk_sigs = {}

    def append(self, sig):
        self.chunks.append(sig)
        self.chunk_sigs.setdefault(sig.adler32, {})
        self.chunk_sigs[sig.adler32][sig.md5] = len(self.chunks) - 1

    def get_chunk(self, chunk):
        adler32 = self.chunk_sigs.get(adler32_chunk(chunk))

        if adler32:
            return adler32.get(md5_chunk(chunk))

        return None

    def __getitem__(self, idx):
        return self.chunks[idx]

    def __len__(self):
        return len(self.chunks)


# Build Chunks from a file
# ------------------------
def checksums_file(fn):
    """
    Returns object with checksums of file
    """
    chunks = Chunks()
    with open(fn) as f:
        while True:
            chunk = f.read(BLOCK_SIZE)
            if not chunk:
                break

            chunks.append(
                Signature(
                    adler32=adler32_chunk(chunk),
                    md5=md5_chunk(chunk)
                )
            )

        return chunks


ServerName = ''
ServerPort = int(sys.argv[2])
ServerAddress = (ServerName, ServerPort)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    serverSocket.bind(ServerAddress)
    serverSocket.listen(1) #queue up 1 connection request
    print('The server is listening')
    connection_socket, addr = serverSocket.accept()
    
    while 1:
        # Server will receive the signal that client wants to update
        msg = connection_socket.recv(1024).decode()  # or 1 byte? try catch?
        if not msg:
            break 

    print("First signal is received")
    # Call checksumfiles to make the NEW block list
    chunkList = checksums_file("NEW")

    # Send checksums_file (which is the hashed list of the file) to client

    
    str_data = json.dumps(chunkList) #Necessary? create str from json-like-Python dict
    serverSocket.sendall(bytes(str_data, encoding="utf-8")) #send entire buffer, sendto() is only for UDP datagram

    # Server receives List from client
    

    # Server will then only send the chunks that are missing from the client ## Refer to hashes


    # Server will assign a header or a tracker to each block size of bytes that it will send to the Client
