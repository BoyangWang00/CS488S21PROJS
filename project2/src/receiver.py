# ----- receiver.py -----

#!/usr/bin/env python
import collections
from socket import *
import sys
import select
import json

host = ''  # "0.0.0.0"
port = int(sys.argv[1])  # 9999
s = socket(AF_INET, SOCK_DGRAM)
s.bind((host, port))


addr = (host, port)
s_buf = 2800

buffer_size = 6
receiver_datagram_buffer = collections.deque(maxlen=buffer_size)
receiver_buffer_round_time = 1


while True:
        #print(len(receiver_datagram_buffer))
        if len(receiver_datagram_buffer) < buffer_size:
            try:
                data, addr = s.recvfrom(s_buf)  # Waiting for first packet from sender
                data_json = json.loads(data)  # deserialize json obj into python dict

                [(header, data)] = list(data_json.items())

                if not data:
                    i = 0
                    for datagram in receiver_datagram_buffer:
                        #print("-----------------write", i)
                        i += 1
                        sys.stdout.write(datagram)
                    receiver_datagram_buffer.clear()
                    exit(2)

                if(int(header)/buffer_size <= receiver_buffer_round_time):
                    position = int(header) % buffer_size
                    if position == 0:
                        position = buffer_size
                    receiver_datagram_buffer.insert(position,data)
                    s.sendto(header.encode(), addr)
                else:
                    pass
                    #do nothing
                s.settimeout(2)

            except timeout:
                i = 0
                for datagram in receiver_datagram_buffer:
                    #print("-----------------write", i)
                    i += 1
                    sys.stdout.write(datagram)
                receiver_datagram_buffer.clear()
                #print("time out")
                exit(2)

        else: 
            #buffer is full and we need to dump 
            assert len(receiver_datagram_buffer) == buffer_size
            i = 0
            for datagram in receiver_datagram_buffer:
                #print("-----------------write", i)
                i += 1
                sys.stdout.write(datagram)
            receiver_buffer_round_time +=1
            receiver_datagram_buffer.clear()
            # s.sendto(header.encode(), addr)

s.close()
