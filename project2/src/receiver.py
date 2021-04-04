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

buffer_size = 20
#receiver_datagram_buffer = collections.deque(maxlen=buffer_size)
receiver_datagram_buffer = {}
for i in range(buffer_size):
    receiver_datagram_buffer[i] = ''
num_of_items_in_buffer = 0
receiver_buffer_round_time = 1

end_of_file = False


while True:
        #print(len(receiver_datagram_buffer))
        if num_of_items_in_buffer < buffer_size:
            try:
                b_data, addr = s.recvfrom(s_buf)  # Waiting for first packet from sender
                data_json = json.loads(b_data)  # deserialize json obj into python dict

                [(header, data)] = list(data_json.items())
                if int(header) <= receiver_buffer_round_time*buffer_size:
                #if we received a packet that we already write out
                #send out ack immediantly
                    s.sendto(header.encode(), addr)

                if((receiver_buffer_round_time-1)*buffer_size< int(header) <= receiver_buffer_round_time*buffer_size):
                    #print("insert", header)
                    position = int(header) % buffer_size
                    if position == 0:
                        position = buffer_size
                    if receiver_datagram_buffer.get(position-1) == '':
                        num_of_items_in_buffer +=1
                        receiver_datagram_buffer[position-1] = data
                    s.sendto(header.encode(), addr)

                else:
                    pass
                    #do nothing

                if b_data == '':
                    end_of_file = True

                s.settimeout(3)

            except timeout:
                i = 0
                for i in range(buffer_size):
                    if receiver_datagram_buffer.get(i) != '':
                        sys.stdout.write(receiver_datagram_buffer.get(i))
                        receiver_datagram_buffer[i] = ''
                        num_of_items_in_buffer -=1
                #print("time out")
                exit()

        else: 
            #buffer is full and we need to dump 
            for i in range(buffer_size):
                #print("line 68")
                #print("-----------------write", i)
                if receiver_datagram_buffer.get(i) != '':
                    sys.stdout.write(receiver_datagram_buffer.get(i))
                    receiver_datagram_buffer[i] = ''
                    num_of_items_in_buffer -=1
                    # for h in range((receiver_buffer_round_time-1)*buffer_size,receiver_buffer_round_time*buffer_size):
                    #     s.sendto(str(h).encode(), addr)
                else:
                    s.sendto(header.encode(), addr)
                    #print(list(receiver_datagram_buffer.keys()))
                    #print("i is",i)
                    #print("BUG!!!!!!!! BUFFER IS NOT FULL")
                    exit(2)
            receiver_buffer_round_time +=1
            # s.sendto(header.encode(), addr)

s.close()
