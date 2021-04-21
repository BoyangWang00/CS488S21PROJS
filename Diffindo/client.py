import collections
import hashlib
import zlib
import socket
import sys

#Client has old file β 
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

#Chunks = a list of Signatures
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


#Client pass in server @ and port in commandline [1][2]
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
serverAddress = (serverName, serverPort)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
      clientSocket.connect(serverAddress)

# Client needs to send server a signal that it wants to update


# Receive List from the server = ChunkList

# client.recvfrom

# Check chunk if it is inside chunkList

# If it is inside, then delete from the copy of the List

# If it is not, offset by 1 and check


checksums =  # decode from the server and you get the list of hashes
# Make a copy of the checksums List = IE. LocalChecksums
localChecksums = checksums.copy()
offset = 0
with open(old_file) as f:
    while True:
        chunk = f.read(BLOCK_SIZE)
        # Until EOF
        if not chunk:
            break
        # Hashes and then checks it against the list that the server sent
        chunk_number = checksums.get_chunk(chunk)

       # If it exists then remove it from the localChecksums
        if chunk_number is not None:
            offset += BLOCK_SIZE
            localChecksums.remove(chunk_number)
            continue
            # Just offset by one, read from that part of the file, and then move on
        else:
            offset += 1
            f.seek(offset)
            continue


# After comparation is done, then send the list to the server

# client.sendto(server)


# If the server or client cuts off, will the connection still be alive or will the client/server know
# Client will now receive the new data from the client

        # If Client decides to pause the download, then you have to make sure to save the header
        # Client will also have to let the server know that it paused or to stop sending
        # Write immediately what we got to a temporary file

        # Once Client resumes, send a signal back to resume downloading
        # Send last header received


# Client will then decode and construct the new file according to checksums' order
