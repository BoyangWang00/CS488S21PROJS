import collections
import hashlib
import zlib
import socket
import sys
import json
import nacl.utils
from nacl.public import PrivateKey, Box

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
        md5_offset = {sig.md5:sig.offset for sig in self.chunks}
        return md5_offset.get(md5)

    def copy(self):
        new_chunck = Chunks()
        for sigs in self.chunks:
            new_chunck.append(sigs)
        return new_chunck

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

def translate_from_Json(chunks,string):
    json_string = json.loads(string)
    for sigs in json_string.get("chunks"):
        chunks.append(
            Signature(
                adler32 = sigs[1],
                md5=sigs[0],
                offset=sigs[2]
                )
            )
    print("return_chunk is ", chunks)


ServerName = sys.argv[1]
ServerPort = int(sys.argv[2])
ServerAddress = (ServerName, ServerPort)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    serverSocket.bind(ServerAddress)
    serverSocket.listen(1)  # queue up 1 connection request
    print('The server is listening')
    connection_socket, addr = serverSocket.accept()

    # Server will receive the signal that client wants to update
    pkClient = connection_socket.recv(1024).decode()  # or 1 byte? try catch?
    print("receive msg is client public key: ", pkClient)

    #ENCRYPTION: Move it here bc just received pkClient
    skServer = PrivateKey.generate()
    pkServer = skServer.public_key
    server_box = Box(skServer, pkClient)

    print("First signal public key is received")
    # Call checksumfiles to make the NEW block list
    chunkList = checksums_file("NEW")
    print("chunklist is ",chunkList)
    json_string = {'chunks':chunkList.chunks,'chunk_sigs':chunkList.chunk_sigs}
    print("json_string",json_string)

    # Send checksums_file (which is the hashed list of the file) to client

 
    str_data = json.dumps(json_string)
    #ENCRYPTION:
    encrypted = server_box.encrypt(str_data.encode)
    connection_socket.sendall(encrypted.encode())


    # send entire buffer, sendto() is only for UDP datagram
    #connection_socket.sendall(str_data.encode())
    
    # singnal to infor client that no more data is sent
    connection_socket.sendall('-1'.encode())

    # Server receives List from client
    # receive request chuncks from client

    received_request = b''
    while True:
        # call a while loop to receve all the data send by server,
        # if server reach to EOF, serversocket.recv() will return 0, break the loop
        data = connection_socket.recv(1024)  # how many B recv?
        print("data is ", data)
        print("last two digit is: ",data.decode()[-2:])
        received_request += data
        if data.decode()[-2:] == '-1':
            break
    print("The whole received data is ",received_request)

    #convert received request into Chunks class

    request_checksums = Chunks()
    translate_from_Json(request_checksums,received_request[:-2])

    # find the offset of the chuncks and form offset list
    # .Chunks should not be iterable
    offset_list = [chunkList.get_offset(signature.md5)
                   for signature in request_checksums.chunks]
    print("offset list is ", offset_list)

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
                print("send chunck ", chunk,'end')
                connection_socket.sendall(chunk.encode())

        print("send last chunck ", last_chunk)
        connection_socket.sendall(last_chunk.encode())

    # May not need the following steps- BW
    # Server will assign a header or a tracker to each block size of bytes that it will send to the Client
