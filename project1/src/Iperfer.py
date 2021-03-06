import sys
import socket
import time


def iperf_client(sys_argv):
    if(len(sys_argv) > 4):
        print("Error: missing or additional arguments")
        quit()

    if(int(sys_argv[2]) < 1024 or int(sys_argv[2]) > 65535):
        print("Error: port number must be in the range 1024 to 65535")
        quit()

    #print('Argument List:', str(sys_argv))

    HOST = sys_argv[1]
    PORT = int(sys_argv[2])
    s_time = float(sys_argv[3])
    # print(s_time)
    chunk_counter = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        data_chunk = bytearray(1000)
        timeout = time.time() + s_time
        while time.time() < timeout:
            s.sendall(data_chunk)
            chunk_counter += 1
        s.sendall(b'1')
        #print(chunk_counter, "chunks are sent")
    rate = round(chunk_counter/1000/s_time*8,3)
    print('sent={0} KB rate={1} Mbps'. format(str(chunk_counter), str(rate)))
    #print('Received', repr(data))


def iperf_server(sys_argv):
    if(len(sys_argv) > 3):
        print("Error: missing or additional arguments")
        quit()
    if(int(sys_argv[2]) < 1024 or int(sys_argv[2]) > 65535):
        print("Error: port number must be in the range 1024 to 65535")
        quit()
    # Symbolic name meaning all available interfaces
    HOST = ''
    PORT = int(sys_argv[2])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        #print("server socket is listening")
        byte_counter = 0
        conn, addr = s.accept()
        #print("server socket accept")
        with conn:
            #print('Connected by', addr)
            time_start = time.time()
            read_num = 0
            while True:
                read_num += 1
                data = conn.recv(1000)
                if not data:
                    break
                byte_counter += len(data)
                #print("server received data")
            time_end = time.time()
            rate = round(byte_counter/1_000_000/(time_end-time_start)*8,3)
            #print('time passed', (time_end-time_start))
            print('received={0} KB rate={1} Mbps'. format(
                str(round(byte_counter/1000)), str(rate)))


sys_argv = sys.argv

if(sys_argv[1] != '-s'):
    iperf_client(sys_argv)
elif(sys_argv[1] == '-s'):
    iperf_server(sys_argv)
