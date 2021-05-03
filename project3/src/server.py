import collections
import hashlib
import zlib
import socket
import sys
import json
import os
from nacl.public import PrivateKey, Box
from nacl.encoding import Base64Encoder
import base64


# Server has new file α
DATA_BLOCK = 36
HEADER_SIZE = 40
BLOCK_SIZE = DATA_BLOCK+HEADER_SIZE

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
def checksums_file_from_encryped(fn):
    """
    Returns object with checksums of file
    """
    fn_offset = 0
    chunks = Chunks()
    with open(fn,'rb') as f:
        while True:
            chunk = f.read(BLOCK_SIZE)
            if not chunk:
                break

            chunks.append(
                Signature(
                    adler32=adler32_chunk(chunk),
                    md5=md5_chunk(chunk),
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
    #print("return_chunk is ", chunks)


def translate_from_list(chunks,list_local):
    for sigs in list_local:
        chunks.append(
            Signature(
                adler32 = sigs[1],
                md5=sigs[0],
                offset=sigs[2]
                )
            )
    #print("return_chunk is ", chunks)



ServerName = ''
ServerPort = int(sys.argv[1])
#File_path = sys.argv[2]
ServerAddress = (ServerName, ServerPort)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    serverSocket.bind(ServerAddress)
    serverSocket.listen(1)  # queue up 1 connection request
    #print('The server is listening on', ServerPort)
    connection_socket, addr = serverSocket.accept()

    # Server will receive the signal that client wants to update
    client_string = connection_socket.recv(1024).decode()
    File_path, client_option = client_string.split(" ")
    print("File path: ", File_path)
    print("Client option: ", client_option)
    file_name = os.path.basename(File_path)
    # Call checksumfiles to make the NEW block list
    chunkList = checksums_file_from_encryped(File_path)
    #print("chunklist is ",chunkList)
    json_string = {'chunks':chunkList.chunks,'chunk_sigs':chunkList.chunk_sigs}
    #print("json_string",json_string)

    # Send checksums_file_from_encryped (which is the hashed list of the file) to client

    # Necessary? create str from json-like-Python dict
    str_data = json.dumps(json_string)
    # send entire buffer, sendto() is only for UDP datagram
    print("String data: ", str_data)
    connection_socket.sendall(str_data.encode())#need to append -1 by the end of string
    # client wants to either upload or download
    # client_option = serverSocket.recv(1024)
    # signal to inform client that no more data is sent
    connection_socket.sendall('-1'.encode())

    if client_option == "download":

            # server receives requested chuncks from client
            received_request = b''
            while True:
                # call a while loop to receve all the data send by server,
                # if server reach to EOF, serversocket.recv() will return 0, break the loop
                data = connection_socket.recv(1024)  # how many B recv?
                #print("data is ", data)
                #print("last two digit is: ",data.decode()[-2:])
                received_request += data
                if data.decode()[-2:] == '-1': #end of data to receive
                    break
            #print("The whole received data is ",received_request)

            #convert received request into Chunks class

            request_checksums = Chunks()
            translate_from_Json(request_checksums,received_request[:-2])

            # find the offset of the chuncks and form offset list
            # .Chunks should not be iterable
            offset_list = [chunkList.get_offset(signature.md5)
                           for signature in request_checksums.chunks]
            #print("offset list is ", offset_list)

            # Server will only send the chunks that client is requesting for
            # open file again and load requested chuncks by offset and send it over to client
            last_chunk = ''
            with open(File_path,'rb') as f:
                for offset in offset_list:
                    f.seek(offset)
                    chunk = f.read(BLOCK_SIZE)
                    # we shouldn't fall into this branch because requested chuncks is
                    # part of NEW file
                    if not chunk:
                        #print("BLOCK DOESN'T EXIST!")
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
                        #print("send chunck ", chunk,'end')
                        connection_socket.sendall(chunk)
                if last_chunk != '':
                    #print("send last chunck ", last_chunk)
                    connection_socket.sendall(last_chunk)


    elif client_option == "upload":
        # server will receive data_list_to_send, which is the list of data chuncks that server doesn't have
        # server will also receive new_file_list.chunks, which is a list of signatures in order. So that server
        # can re-construct the new file based on this list
        server_received_data = b''
        while True:
            # call a while loop to receve all the data send by server,
            # if server reach to EOF, serversocket.recv() will return 0, break the loop
            data = connection_socket.recv(1024)  # how many B recv?
            print("recevied data is ", data)
            #print("data is ", data)
            #print("last two digit is: ",data.decode()[-2:])
            server_received_data += data
            if data.decode()[-2:] == '-1': #end of data to receive
                print("we recevied the last chunk")
                break
        # translate data into a dictionary {'data_list_to_send':data_list_to_send, 'new_file_list.chunks':new_file_list.chunks}
        print("the string is :",server_received_data.decode())
        json_dict = json.loads(server_received_data[:-2].decode())

        data_chunk_list = json_dict.get("data_list_to_send")
        print("data_chunk_list", data_chunk_list)
        hash_list = Chunks()
        translate_from_list(hash_list,json_dict.get("new_file_list.chunks"))

        print("hash_list", hash_list)

        list_to_write = []
        ith_chunk_in_data_chunk_list = 0
        for block in hash_list.chunks:
            if block.md5 in [items.md5 for items in chunkList.chunks]: 
                #open the file and read chunk data; append data to list_to_write
                offset = hash_list.get_offset(block.md5)
                with open(File_path) as f:
                    f.seek(offset)
                    chunk_data = f.read(BLOCK_SIZE)
                    list_to_write.append(chunk_data)
            else:
                # assume the data_chunk_list has all the missing data in order
                # 
                list_to_write.append(base64.b64decode(data_chunk_list[ith_chunk_in_data_chunk_list]))
                ith_chunk_in_data_chunk_list += 1

        with open("Updated_file"+file_name,"wb") as f:
            for block in list_to_write:
                f.write(block)

        os.rename("Updated_file"+file_name,file_name)
        print("Upload is complete")

        connection_socket.sendall("Upload is complete".encode())


        exit(0)