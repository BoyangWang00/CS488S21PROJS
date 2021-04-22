import collections
import hashlib
import zlib
import socket
import sys
import os

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
Signature = collections.namedtuple('Signature', 'md5 adler32')

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

# def reconstruct_file(OLD, TEMP_LOG, server_list, old_list, temp_log_list):
#     with open('NEW_TEMP', 'w') as new_temp:
#         for block in server_list:
#             if block in old_list:
#                 # find block with offset and write out to new_temp file
#             elif block in temp_log_list:
#                 # find block with offset and write out to new_temp file
#     return new_temp


# Client pass in server @ and port in commandline [1][2]
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
serverAddress = (serverName, serverPort)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
    clientSocket.connect(serverAddress)
    # clientSocket.setblocking(0) # client non-blocking to receive list from server (?)
    # Client needs to send server a signal that it wants to update
    clientSocket.send('s'.encode())

    # Receive List from the server = ChunkList
    received_data = b''
    while True:
        # call a while loop to receve all the data send by server,
        # if server reach to EOF, clientSocket.recv() will return 0, break the loop
        data = clientSocket.recv(1024)  # how many B recv?
        if data:
            received_data += data
        else:
            break


# Check chunk if it is inside chunkList

# If it is inside, then delete from the copy of the List

# If it is not, offset by 1 and check

    # decode from the server and you get the list of hashes
    checksums = json.loads(received_data.decode(
        encoding='utf-8'))  # Returns the list
    # Make a copy of the checksums List = IE. localChecksums
    localChecksums = checksums.copy()
    list_to_write = []
    offset = 0
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
                offset += BLOCK_SIZE
                localChecksums.remove(chunk_number)
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
                    localChecksums.remove(chunk_number)
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

    request_list = json.dumps(localChecksums)
    # Why not sendall???
    clientSocket.send(request_list.encode())

    while localChecksums:

        # client start to receiv data chuncks from server
        received_chunck = b''
        while True:
            # call a while loop to receve all the data send by server,
            # if server reach to EOF, clientSocket.recv() will return 0, break the loop
            data = clientSocket.recv(1024)  # how many B recv?
            if data and data.decode() != '':
                received_data += data

                # Turn data you received into a Hash into a new variable

                # Check the client list and see if it's inside the client's list
                # If it isn't, then check the server's list to see if it's inside
                # If it's inside the servers, then find the position
                if x in request_list:
                    pass
                else:
                    if x in server_list:
                        # save position of new data to updatae
                        updateAt = server_list.index(x)
                    else:
                        print("{} is not in server list".format(chunk))
                # Left off here
                list_to_write.append(index, data.decode())

                # Using the position, append the data into the position for list_to_write

            else:
                break
    with open('OLD', 'w') as write_out:
        # Converts to string
        list_to_write = "".join(list_to_write)
        # Writes entire thing to file
        write_out.write(list_to_write)

        # if file_size%BLOCK_SIZE == 0, no short chunks in the file
        # append received data by the end
        # else reset the offset to the end of last whole chunk
        # overwrite the short chunck
        file_size = os.stat('TEMP_LOG').st_size
        if file_size % BLOCK_SIZE == 0
        with open('TEMP_LOG', 'a') as temp_log:
            temp_log.write(received_data.decode())
        else:
            with open('TEMP_LOG', 'r+') as temp_log:
                temp_log.seek(file_size//BLOCK_SIZE*BLOCK_SIZE)
                temp_log.write(received_data.decode())

        # after write out the received chunk data, remove it from list
        localChecksums.remove(checksums.get_chunk(received_data))

# at this point, everything client requested for is saved in OLD_TEMP file,
# we can close the TCP connection and start re-contruct the NEW file at client's end

new_temp = reconstruct_file(
    OLD, TEMP_LOG, checksums, checksums_file(OLD), checksums_file(TEMP_LOG))

# TODO!!
# rename new_temp to replace OLD file
# delete OLD_TEMP file


# Client will then decode and construct the new file according to checksums' order
