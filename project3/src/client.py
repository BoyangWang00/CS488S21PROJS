import collections
import hashlib
import zlib
import socket
import sys
import os
import json

# Client has old file β
BLOCK_SIZE = 4

# Hasher
# Helper functions
# ----------------


def md5_chunk(chunk):
    """
    Returns strong md5 checksum for chunk
    """
    m = hashlib.md5()
    m.update(chunk)
    return m.hexdigest()


def adler32_chunk(chunk):
    """
    Returns weak adler32 checksum for chunk
    """
    return zlib.adler32(chunk)


# Checksum objects
# ----------------
Signature = collections.namedtuple('Signature', 'md5 adler32 offset')

# Chunks = a list of Signatures


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

    def remove(self, sig):
        self.chunks.remove(sig)
        self.chunk_sigs[sig.adler32].pop(sig.md5)
        if self.chunk_sigs[sig.adler32] == {}:
            self.chunk_sigs.pop(sig.adler32)

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


# TODO: FINISH THIS FUNCTION
# reconstruct the NEW file by using OLD file, OLD_TEMP file and checksums list received from server

def reconstruct_file(OLD, TEMP_LOG, server_list, old_file_list):
    print("start construct the file")
    print("server_list",server_list, "length is", len(server_list))
    print()
    temp_log_list = checksums_file(TEMP_LOG)

    old = open(OLD,'r')
    temp_log = open(TEMP_LOG,'r')
    with open('CONSTRUCT_FILE', 'w') as constructer:

        for signature in server_list.chunks:
            print('sig',signature)
            if signature.md5 in [items.md5 for items in old_file_list.chunks]:
                # find block with offset and write out to new_temp file
                offset = old_file_list.get_offset(signature.md5)
                print('offset of old file', offset)
                old.seek(offset)
                data = old.read(BLOCK_SIZE)
                print('data from old file', data)
                constructer.write(data)

            if signature.md5 in [items.md5 for items in temp_log_list.chunks]:
                # find block with offset and write out to new_temp file
                offset = temp_log_list.get_offset(signature.md5)
                print('offset of temp_log', offset)
                temp_log.seek(offset)
                data = temp_log.read(BLOCK_SIZE)
                print("data from temp_log", data)
                constructer.write(data)
    
    old.close()
    temp_log.close()

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

# Client pass in server @ and port in commandline [1][2]
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
serverAddress = (serverName, serverPort)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
    clientSocket.connect(serverAddress)
    # clientSocket.setblocking(0) # client non-blocking to receive list from server (?)
    # Client needs to send server a signal that it wants to update
    clientSocket.sendall('s'.encode())

    # Receive List from the server = ChunkList
    received_data = b''
    while True:
        # call a while loop to receve all the data send by server,
        # if server reach to EOF, clientSocket.recv() will return '-1', break the loop
        data = clientSocket.recv(1024)  # how many B recv?
        print("data is ", data)
        print("last two digit is: ",data.decode()[-2:])
        received_data += data
        if data.decode()[-2:] == '-1':
            break
    print("The whole received data is ",received_data)

# decode from the server and you get the list of hashes
    checksums = Chunks()
    print(checksums)
# need to re-construct Chunks object based on json string that we received
    translate_from_Json(checksums,received_data.decode()[:-2])
    json_string = {'chunks':checksums.chunks,'chunk_sigs':checksums.chunk_sigs}
    print("checksums after translate_from_Json", json_string)

# Check chunk if it is inside chunkList

# If it is inside, then delete from the copy of the List

# If it is not, offset by 1 and check

    # Make a copy of the checksums List = IE. localChecksums
    localChecksums = checksums.copy()
    list_to_write = []
    offset = 0
    old_file_list = Chunks()
    with open('OLD') as f:
        while True:
            chunk = f.read(BLOCK_SIZE)
            # list_to_write.append(chunk)
            # Until EOF
            if not chunk:
                break
            # Hashes and then checks it against the list that the server sent
            chunk_number = checksums.get_chunk(chunk.encode())

           # If it exists then remove it from the localChecksums
            if chunk_number is not None:

                localChecksums.remove(checksums.__getitem__(chunk_number))
                old_file_list.append(
                Signature(
                    adler32=adler32_chunk(chunk.encode()),
                    md5=md5_chunk(chunk.encode()),
                    offset=offset
                )
            )
                offset += BLOCK_SIZE
                # continue
                # Just offset by one, read from that part of the file, and then move on
            else:
                offset += 1
                f.seek(offset)
                # continue

# TODO: need to add code to check whether there is a temp_log file under current directry.
# if there is, which means the download was interrupted last time, we need to check both OLD file
# and TEMP_LOG file
    try:
        with open('TEMP_LOG') as temp_log:
            while True:
                chunk = temp_log.read(BLOCK_SIZE)
                # Until EOF
                if not chunk:
                    break
                # Hashes and then checks it against the list that the server sent
                chunk_number = checksums.get_chunk(chunk.encode())

               # If it exists then remove it from the localChecksums
                if chunk_number is not None:
                    offset += BLOCK_SIZE
                    localChecksums.remove(checksums.__getitem__(chunk_number))
                    # continue
                    # Just offset by one, read from that part of the file, and then move on
                else:
                    # continue
                    print("download was interrupted before")
                    # TEMP_LOG should not fall into this branch unless it reach the last short block
                    # because everything else in TEMP_LOG are requested blocks from server
    except OSError:
        print('no temp_log in current directry')


# After comparation is done, then send the request list to the server

# client.sendto(server)
    json_format = {'chunks':localChecksums.chunks,'chunk_sigs':localChecksums.chunk_sigs}
    request_list = json.dumps(json_format)
    clientSocket.sendall(request_list.encode())
# singnal to infor client that no more data is sent
    clientSocket.sendall('-1'.encode())

    while localChecksums:

        # client start to receiv data chuncks from server
        # call a while loop to receve all the data send by server,
        # if server reach to EOF, clientSocket.recv() will return 0, break the loop
        data = clientSocket.recv(BLOCK_SIZE)  # how many B recv?
        print("recevied data is :",data.decode())
        if data and data.decode() != '':
            # if file_size%BLOCK_SIZE == 0, no short chunks in the file
            # append received data by the end
            # else reset the offset to the end of last whole chunk
            # overwrite the short chunck

            if not os.path.exists('TEMP_LOG'):
                with open('TEMP_LOG','w'):
                    pass
            with open('TEMP_LOG', 'r+') as temp_log:
                file_size = os.stat('TEMP_LOG').st_size
                temp_log.seek(file_size//BLOCK_SIZE*BLOCK_SIZE)
                temp_log.write(data.decode())

            print("localChecksums length",len(localChecksums))
            print("checksums length",len(checksums))
            print("localChecksums",localChecksums.chunks)
            print("checksums data", checksums.get_chunk(data))
            # have a bug!!!!! get chunck data doesn't exit in local checksums
            localChecksums.remove(checksums.chunks[checksums.get_chunk(data)])

# at this point, everything client requested for is saved in OLD_TEMP file,
# we can close the TCP connection and start re-contruct the NEW file at client's end


reconstruct_file('OLD', 'TEMP_LOG', checksums,old_file_list)
#we write out the whole contructor file now


# rename CONSTRUCT_FILE to replace OLD file
# delete TEMP_LOG file
os.rename(r'CONSTRUCT_FILE',r'OLD')

os.remove('TEMP_LOG')
