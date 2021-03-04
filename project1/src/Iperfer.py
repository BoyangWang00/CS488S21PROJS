import sys
import socket
import time


def iperf_client(sys_argv):
    if(len(sys_argv) != 4):
        print("Error: missing or additional arguments")
        quit()

    if(int(sys_argv[2]) < 1024 or int(sys_argv[2]) > 65535):
        print("Error: port number must be in the range 1024 to 65535")
        quit()

    #print('Argument List:', str(sys_argv))

    HOST = sys_argv[1]
    PORT = int(sys_argv[2])
    s_time = float(sys_argv[3])
    print(s_time)
    chunk_counter = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        data_chunk = bytearray(1000)
        timeout = time.time() + s_time
        while (1):
            s.sendall(data_chunk)
            chunk_counter += 1
            # print(chunk_counter)
            data = s.recv(1000)
            if time.time() > timeout:
                s.sendall(b'1')
                # print(time.time())
                print("time is out")
                break
        s.close()
        print(chunk_counter, "chunks are sent")
        rate = chunk_counter/1000/s_time
    print('sent={0} KB rate={1} Mbps'. format(str(chunk_counter), str(rate)))
    return
    #print('Received', repr(data))


def iperf_server(sys_argv):
    if(len(sys_argv) != 3):
        print("Error: missing or additional arguments")
        quit()
    if(int(sys_argv[2]) < 1024 or int(sys_argv[2]) > 65535):
        print("Error: port number must be in the range 1024 to 65535")
        quit()
    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = int(sys_argv[2])
    chunk_counter = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("server socket is listening")
        while True:
            conn, addr = s.accept()
            print("server socket accept")
            with conn:
                print('Connected by', addr)
                time_start = time.time()
                while True:
                    data = conn.recv(1000)
                    chunk_counter += 1
                    #print("server received data")
                    data = data.upper()
                    if data == (b'1'):
                        time_end = time.time()
                        rate = chunk_counter/1000/(time_end-time_start)
                        print('time passed', (time_end-time_start))
                        print('received={0} KB rate={1} Mbps'. format(
                            str(chunk_counter), str(rate)))
                        return
                    conn.sendall(data)


sys_argv = sys.argv

if(sys_argv[1] != '-s'):
    iperf_client(sys_argv)
elif(sys_argv[1] == '-s'):
    iperf_server(sys_argv)
