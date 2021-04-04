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

buffer_size = 10
# receiver_datagram_buffer = collections.deque(maxlen=buffer_size)
receiver_datagram_buffer = {}
for i in range(buffer_size):
    receiver_datagram_buffer[i] = ''
num_of_items_in_buffer = 0
receiver_buffer_round_time = 1


while True:
    try:
        # Waiting for first packet from sender
        b_data, addr = s.recvfrom(s_buf)
        # deserialize json obj into python dict
        data_json = json.loads(b_data)
        [(header, data)] = list(data_json.items())
        index = int(header) % buffer_size
        # Put it inside of buffer_size
        if receiver_datagram_buffer.get(index) == '':
            receiver_datagram_buffer[index] = data
            num_of_items_in_buffer += 1
            s.sendto(header.encode(), addr)
        # print(len(receiver_datagram_buffer))
        if num_of_items_in_buffer > 5 or num_of_items_in_buffer < buffer_size:
            for i in range(buffer_size):
                if receiver_datagram_buffer.get(i) != '':
                    # print("try")
                    sys.stdout.write(receiver_datagram_buffer.get(i))
                    receiver_datagram_buffer[i] = ''
                    num_of_items_in_buffer -= 1
                else:
                    break

        s.settimeout(3)
    except timeout:
        for i in range(buffer_size):
            if receiver_datagram_buffer.get(i) != '':
                # print("timeout")
                sys.stdout.write(receiver_datagram_buffer.get(i))

            else:
                pass
        exit()


s.close()
