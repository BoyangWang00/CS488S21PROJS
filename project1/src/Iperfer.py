import sys
import socket
import time

if(len(sys.argv) != 4):
    print("Error: missing or additional arguments")
    quit()

if(int(sys.argv[2])<1024 or int(sys.argv[2])>65535):
    print("Error: port number must be in the range 1024 to 65535")
    quit()

#print('Argument List:', str(sys.argv))

HOST = sys.argv[1]
PORT = int(sys.argv[2])
s_time = float(sys.argv[3])
print(s_time)
chunk_counter = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data_chunk = bytearray(1000)
    timeout = time.time() + s_time
    while (1):
        s.sendall(data_chunk)
        chunk_counter += 1
        #print(chunk_counter)
        data = s.recv(1024)
        if time.time() > timeout:
            #print(time.time())
            print("time is out")
            break
    s.close()
    print(chunk_counter, "chunks are sent")
    rate = chunk_counter/1000/s_time
print('sent = {0} KB rate = {1} Mbps'. format(str(chunk_counter), str(rate)))
#print('Received', repr(data))