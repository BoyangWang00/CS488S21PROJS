import collections
import hashlib
import zlib
import socket
import sys
import os
import json
import time
import nacl.secret
import nacl.utils
from nacl.public import PrivateKey, Box
from nacl.encoding import Base64Encoder
import base64

# Client has old file β
BLOCK_SIZE = 36
clientSecretKey = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
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
        if sig in self.chunks:
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
        return len(self.chunks)

# Build Chunks from a file
# ------------------------


def checksums_file(fn, client_path):
    """
    Returns object with checksums of file
    """
    fn_offset = 0
    chunks = Chunks()
    global key, nonce
    key, nonce = retrieveClientKey(client_path)
    print("Key is : {} Nonce is: {}", key, nonce)
    print("FN is", fn)
    with open(fn) as f:
        while True:
            chunk = f.read(BLOCK_SIZE)
            # Send client public key
            print("Base64 Decoded: ", base64.b64decode(key))
            clientBox = nacl.secret.SecretBox(base64.b64decode(key))
            # Encrypt Box
            print("Nonce is ", nonce)
            print("chunk is ", chunk)
            encrypted = clientBox.encrypt(
                chunk.encode(), base64.b64decode(nonce))
            # Receiving the encryptedBox
            # serverMessage = serverBox.decrypt(box)
            # serverMessage = serverMessage.decode('utf-8')
            # print()

            if not chunk:
                break

            # Turn encrypted box into hash and put hash into list
            chunks.append(
                Signature(
                    adler32=adler32_chunk(encrypted),
                    md5=md5_chunk(encrypted),
                    offset=fn_offset
                )
            )

            fn_offset += BLOCK_SIZE

        return chunks


def reconstruct_file(OLD, TEMP_LOG, server_list, old_file_list, client_path):
    # print("start construct the file")
    # print("server_list",server_list, "length is", len(server_list))
    print()
    if os.path.exists(TEMP_LOG):
        temp_log_list = checksums_file(TEMP_LOG, client_path)

    old = open(OLD, 'r')
    if os.path.exists(TEMP_LOG):
        temp_log = open(TEMP_LOG, 'r')
    with open(old_file_name+'CONSTRUCT_FILE', 'w') as constructer:

        for signature in server_list.chunks:
            # print('sig',signature)
            if signature.md5 in [items.md5 for items in old_file_list.chunks]:
                # find block with offset and write out to new_temp file
                offset = old_file_list.get_offset(signature.md5)
                # print('offset of old file', offset)
                old.seek(offset)
                data = old.read(BLOCK_SIZE)
                # print('data from old file', data)
                constructer.write(data)
            if os.path.exists(TEMP_LOG):
                if signature.md5 in [items.md5 for items in temp_log_list.chunks]:
                    # find block with offset and write out to new_temp file
                    offset = temp_log_list.get_offset(signature.md5)
                    # print('offset of temp_log', offset)
                    temp_log.seek(offset)
                    data = temp_log.read(BLOCK_SIZE)
                    # print("data from temp_log", data)
                    constructer.write(data)

    old.close()
    if os.path.exists(TEMP_LOG):
        temp_log.close()


def translate_from_Json(string):
    local_chunks = Chunks()
    print("Json Loads String: ", string)
    json_string = json.loads(string)
    for sigs in json_string.get("chunks"):
        local_chunks.append(
            Signature(
                adler32=sigs[1],
                md5=sigs[0],
                offset=sigs[2]
            )
        )
    # print("return_chunk is ", local_chunks)
    return local_chunks

# Assigns client key and nonce


def retrieveClientKey(client_path):
    if not os.path.exists(client_path):
        # if exists, write to clientInfo file and return key and nonce
        with open(client_path, 'w'):
            assert os.path.exists(client_path)
            pass
    # write to clientInfo file
        with open(client_path, 'rb+') as client:
            key = nacl.utils.random(
                nacl.secret.SecretBox.KEY_SIZE)
            nonce = nacl.utils.random(
                nacl.secret.SecretBox.NONCE_SIZE)
            b64_key = base64.b64encode(key)
            b64_nonce = base64.b64encode(nonce)
            print("Key is {} nonce is {}", key, nonce)
            print("Base64 Key is {} nonce is {}", b64_key, b64_nonce)
            key_nonce = (b64_key, b64_nonce)
            client_bytes_join = b"\n".join(key_nonce)
            client.write(client_bytes_join)
    else:
        if os.path.exists(client_path):
            with open(client_path, mode='rb+') as client:
                key_nonce = client.readlines()

                print("Client read ", key_nonce)
                # key_nonce = (key1, nonce2)

                # key_nonce = (key, nonce)
    return key_nonce


# Client pass in server @ and port in commandline [1][2]
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
serverAddress = (serverName, serverPort)
option = sys.argv[3]  # down or upload
#src_path_new = sys.argv[4] #
# des_path_old = sys.argv[5]


# Take user input
src_path_new = input("Enter source file path:")
des_path_old = input("Enter destination file path:")
old_file_name = os.path.basename(des_path_old)
directry_path = os.path.dirname(des_path_old)
temp_log_path = os.path.join(directry_path, old_file_name+'TEMP_LOG')
client_name = os.path.basename(des_path_old)
client_dir_name = os.path.dirname(des_path_old)
client_path = os.path.join(client_dir_name, 'clientInfo')
if option == 'download':

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
        # print("client is trying to connect to ", serverPort)
        clientSocket.connect(serverAddress)

        # Client needs to send server a signal that it wants to update
        signal = (src_path_new, option)
        signal = " ".join(map(str, signal))
        clientSocket.sendall(signal.encode())

        # Receive List from the server = ChunkList
        received_data = b''
        while True:
            # call a while loop to receve all the data send by server,
            # if server reach to EOF, clientSocket.recv() will return '-1', break the loop
            data = clientSocket.recv(1024)
            # print("data is ", data)
            # print("last two digit is: ",data.decode()[-2:])
            print('data ', data)
            received_data += data
            if data.decode()[-2:] == '-1':
                break
        # print("The whole received data is ",received_data)

        # TODO: Decrypt each box

    # decode from the server and you get the list of hashes
    # need to re-construct Chunks object based on json string that we received
        checksum_string = received_data.decode()
        checksums = translate_from_Json(checksum_string[:-2])
        # print("here is the checksums!!!!!!",checksums)
        json_string = {'chunks': checksums.chunks,
                       'chunk_sigs': checksums.chunk_sigs}
        # print("checksums after translate_from_Json", json_string)

    # Check chunk if it is inside chunkList

    # If it is inside, then delete from the copy of the List

    # If it is not, offset by 1 and check

        # Make a copy of the checksums List = IE. localChecksums
        localChecksums = checksums.copy()
        list_to_write = []
        offset = 0
        key, nonce = retrieveClientKey(client_path)
        old_file_list = Chunks()
        with open(des_path_old) as f:
            while True:
                chunk = f.read(BLOCK_SIZE)
                # list_to_write.append(chunk)
                # Until EOF
                print("Base64 Decoded: ", base64.b64decode(key))
                clientBox = nacl.secret.SecretBox(base64.b64decode(key))
                # Encrypt Box
                print("Nonce is ", nonce)
                print("chunk is ", chunk)
                encrypted = clientBox.encrypt(
                    chunk.encode(), base64.b64decode(nonce))
                if not chunk:
                    break
                # Make the boxes here and then we can figure out the adler32 and compare
              # Hashes and then checks it against the list that the server sent

                chunk_number = checksums.get_chunk(encrypted)

               # If it exists then remove it from the localChecksums
            if chunk_number is not None:
                # print(chunk_number)
                # print(chunk)

                localChecksums.remove(checksums.__getitem__(chunk_number))
                old_file_list.append(
                    Signature(
                        adler32=adler32_chunk(chunk.encode()),
                        md5=md5_chunk(chunk.encode()),
                        offset=offset
                    )
                )
                offset += BLOCK_SIZE
                # Just offset by one, read from that part of the file, and then move on
            else:
                offset += 1  # if no match
                f.seek(offset)

            shopping_list_len_before_templog = len(localChecksums.chunks)

    # TODO: need to add code to check whether there is a temp_log file under current directry.
    # if there is, which means the download was interrupted last time, we need to check both OLD file
    # and TEMP_LOG file
        try:
            with open(temp_log_path) as temp_log:
                while True:
                    chunk = temp_log.read(BLOCK_SIZE)
                    # Until EOF
                    if not chunk:
                        break
                    # Hashes and then checks it against the list that the server sent
                   # print(chunk)
                    chunk_number = checksums.get_chunk(chunk.encode())

                   # If it exists then remove it from the localChecksums
                    if chunk_number is not None:
                        offset += BLOCK_SIZE
                        localChecksums.remove(
                            checksums.chunks[checksums.get_chunk(chunk.encode())])
                        # continue
                        # Just offset by one, read from that part of the file, and then move on
                    else:
                        continue
                        # print("download was interrupted before")
                        # TEMP_LOG should not fall into this branch unless it reach the last short block
                        # because everything else in TEMP_LOG are requested blocks from server
        except OSError:
           # print('no temp_log in current directry')
            pass

        # for test porpose only, if CHECK_SHOPPING_LIST_SHOULD_BE_SHORT is on, which means we preset the
        # temp_log in directory. so shopping list should be shorter than shopping_list_len_before_templog
        if os.environ.get('CHECK_SHOPPING_LIST_SHOULD_BE_SHORT') == '1':
            # print(len(localChecksums.chunks), shopping_list_len_before_templog)
            assert (len(localChecksums.chunks) <
                    shopping_list_len_before_templog)
    # After comparation is done, then send the request list to the server
    # client.sendto(server)
        json_format = {'chunks': localChecksums.chunks,
                       'chunk_sigs': localChecksums.chunk_sigs}
        request_list = json.dumps(json_format)
        clientSocket.sendall(request_list.encode())
    # singnal to infor client that no more data is sent
        clientSocket.sendall('-1'.encode())

        while localChecksums:

            # client start to receiv data chuncks from server
            # call a while loop to receive all the data send by server,
            # if server reach to EOF, clientSocket.recv() will return 0, break the loop
            data = clientSocket.recv(BLOCK_SIZE)  # how many B recv?
            # print("recevied data is :",data.decode())
            if data and data.decode() != '':
                # if file_size%BLOCK_SIZE == 0, no short chunks in the file
                # append received data by the end
                # else reset the offset to the end of last whole chunk
                # overwrite the short chunck
                # print("is file in the path " + str(os.path.exists(temp_log_path) ))
                if not os.path.exists(temp_log_path):
                    with open(temp_log_path, 'w'):
                        assert os.path.exists(temp_log_path)
                        # print("created ", temp_log_path)
                        pass
                with open(temp_log_path, 'r+') as temp_log:
                    file_size = os.stat(temp_log_path).st_size
                    temp_log.seek(file_size//BLOCK_SIZE*BLOCK_SIZE)
                    temp_log.write(data.decode())

                # print("localChecksums length",len(localChecksums))
                # print("checksums length",len(checksums))
                # print("localChecksums",localChecksums.chunks)
                # print("checksums data", checksums.get_chunk(data))

                # have a bug!!!!! get chunck data doesn't exit in local checksums
                # ^ is this still an issue?

                # print("Printing local checksums: \n", localChecksums)
                # print("Length of local checksums:", len(localChecksums))
                try:
                    print("Checksums.get_chunk(data) =",
                          checksums.chunks[checksums.get_chunk(data)])
                    localChecksums.remove(
                        checksums.chunks[checksums.get_chunk(data)])
                except TypeError:
                    print("Type Error :(")
                    print("Data:", data)
                    print("Data Type:", type(data))

    # at this point, everything client requested for is saved in OLD_TEMP file,
    # we can close the TCP connection and start re-contruct the NEW file at client's end

    reconstruct_file(des_path_old, temp_log_path,
                     checksums, old_file_list, client_path)
    # we write out the whole contructor file now

    # rename CONSTRUCT_FILE to replace OLD file
    # delete TEMP_LOG file
    os.rename(old_file_name+'CONSTRUCT_FILE', des_path_old)

    if os.path.exists(temp_log_path):
        os.remove(temp_log_path)
    print(des_path_old, "download completed")
    exit()
elif option == 'upload':
    # send upload request to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
        # print("client is trying to connect to ", serverPort)
        clientSocket.connect(serverAddress)

        # encrypted = box.encrypt(message, nonce)
        # Client needs to send server a signal that it wants to update
        signal = (des_path_old, option)
        signal = " ".join(map(str, signal))
        print("Signal is ", signal)
        clientSocket.sendall(signal.encode())
        # print("inside upload with statement")
        received_data = b''

        while True:
            # print("inside while true statement")
            data = clientSocket.recv(1024)
            # clientSocket.sendall(option)
            print("Data is ", data)
            print("data decoded is:", data.decode())
            received_data += data  # OLD file list
            print("Recieved data = ", received_data)
            if data.decode()[-2:] == '-1':
                break

        # Compare received OLD list with current client NEW list:
        old_checksums = translate_from_Json(received_data.decode()[:-2])
        json_string = {'chunks': old_checksums.chunks,
                       'chunk_sigs': old_checksums.chunk_sigs}

        localChecksums = old_checksums.copy()
        data_list_to_send = []
        offset = 0
        new_file_name = os.path.basename(src_path_new)  # (?)
        # client's new longer hashlist
        print("New File Path name: ", new_file_name)
        new_file_list = checksums_file(new_file_name, client_path)
        print("Hashed Data to send: ", new_file_list.chunks)

        # print("New file name is ", new_file_name)
        # print("New file list is ", new_file_list)

        key1, nonce1 = retrieveClientKey(client_path)

        # Create a list of actual data blocks that need to be sent over to server
        for block in new_file_list.chunks:
            # print("inside for block in new_file_list loop")
            if block.md5 not in [items.md5 for items in localChecksums.chunks]:
                # new block not in old list
                with open(src_path_new) as f:
                    f.seek(block.offset)
                    chunk = f.read(BLOCK_SIZE)
                    # Create client box with key
                    print("Key Value is: ", base64.b64decode(key1))
                    print("Key Type is: ", type(key))
                    print("Nonce Value is: ", base64.b64decode(nonce1))
                    print("Nonce Type is: ", type(nonce))
                    clientBox = nacl.secret.SecretBox(base64.b64decode(key1))
                    # Encrypt Box with chunk and nonce
                    encrypted = clientBox.encrypt(
                        chunk.encode(), base64.b64decode(nonce1))
                    b64_encrypted = base64.b64encode(encrypted)

                    if not chunk:
                        # if no data
                        break
                    data_list_to_send.append(b64_encrypted.decode())
        print("Data List to send is: ", data_list_to_send)
        # if signature.md5 in [items.md5 for items in temp_log_list.chunks]:

        # Send the data blocks and offset list to reconstruct
        to_send = {'data_list_to_send': data_list_to_send,
                   'new_file_list.chunks': new_file_list.chunks}
        data_json = json.dumps(to_send)
        clientSocket.sendall(data_json.encode())
        time.sleep(1)
        clientSocket.sendall('-1'.encode())

        # client should receive "Upload is finished" and print it out
        finish_signal = clientSocket.recv(1024)
        print(finish_signal.decode())


else:
    print("wrong option")
