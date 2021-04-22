import collections
import hashlib
import zlib
import socket
import sys
import json

# Server has new file α
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
Signature = collections.namedtuple('Signature', 'md5 adler32 offset')


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

    def get_offset(self, md5):
        offset = [
            self.chunks.offset for signature in self.chunks if self.chunks.md5 == md5]
        assert len(offset) == 1
        return offset[0]

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
    fn_offset = 0
    chunks = Chunks()
    with open(fn) as f:
        while True:
            chunk = f.read(BLOCK_SIZE)
            if not chunk:
                break

            chunks.append(
                Signature(
                    adler32=adler32_chunk(chunk.encode()),
                    md5=md5_chunk(chunk.encode()),
                    offset=fn_offset
                )
            )

            fn_offset += BLOCK_SIZE

        return chunks


ServerName = ''
ServerPort = int(sys.argv[2])
ServerAddress = (ServerName, ServerPort)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    serverSocket.bind(ServerAddress)
    serverSocket.listen(1)  # queue up 1 connection request
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

    # Necessary? create str from json-like-Python dict
    str_data = json.dumps(chunkList)
    # send entire buffer, sendto() is only for UDP datagram
    connection_socket.sendall(bytes(str_data, encoding="utf-8"))

    # Server receives List from client

    received_request = b''
    while True:
        # call a while loop to receve all the data send by server,
        # if server reach to EOF, serversocket.recv() will return 0, break the loop
        data = connection_socket.recv(1024)
        if data:
            received_request += data
        else:
            break
    # receive request chuncks from client
    request_checksums = json.loads(received_request.decode(encoding="utf-8"))
    # find the offset of the chuncks and form offset list
    # .Chunks should not be iterable
    offset_list = [chunkList.get_offset(signature.md5)
                   for signature in request_checksums.chunks]

    # Server will only send the chunks that client is requesting for
    # open file again and load requested chuncks by offset and send it over to client
    last_chunk = ''
    with open('NEW') as f:
        for offset in offset_list:
            f.seek(offset)
            chunk = f.read(BLOCK_SIZE)
            # we shouldn't fall into this branch because requested chuncks is
            # part of NEW file
            if not chunk:
                print("BLOCK DOESN'T EXIST!")
                assert(False)
            # if len(chunk) is less than block size, we need to hold this block
            # send it over at last
            # client will write out the received chunks to a temp file upon receiving
            # if client will always use len(tempfile)%BLOCK_SIZE == 0 to check whether
            # the writing process is interruped in the middle or not
            # thus we cannot send over the short chuncks until we finish sending others
            if len(chunk) < BLOCK_SIZE:
                last_chunk = chunk
                continue
            else:

                connection_socket.sendall(chunk.encode())

        # Why do we need this?
        connection_socket.sendall(last_chunk.encode())

    # May not need the following steps- BW
    # Server will assign a header or a tracker to each block size of bytes that it will send to the Client
