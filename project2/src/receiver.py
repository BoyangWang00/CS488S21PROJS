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
#receiver_datagram_buffer = collections.deque(maxlen=buffer_size)
receiver_datagram_buffer = {}
for i in range(buffer_size):
    receiver_datagram_buffer[i] = ''
num_of_items_in_buffer = 0
receiver_buffer_round_time = 1


def write_to_file(num_of_items_in_buffer):
    # If the # of items in list is buffer - 1
    for i in range(buffer_size):

        sys.stdout.write(receiver_datagram_buffer.get(i))
        receiver_datagram_buffer[i] = ''
        num_of_items_in_buffer -= 1


while True:
    # print(len(receiver_datagram_buffer))
    if num_of_items_in_buffer < buffer_size:
        try:
            # Waiting for first packet from sender
            b_data, addr = s.recvfrom(s_buf)
            # deserialize json obj into python dict
            data_json = json.loads(b_data)

            [(header, data)] = list(data_json.items())

            if b_data:
                position = int(header) % buffer_size

                if receiver_datagram_buffer.get(position) == '':
                    #print("Inside if receiver_datagram ", header)
                    num_of_items_in_buffer += 1
                    receiver_datagram_buffer[position] = data
                    #print(receiver_datagram_buffer[position])
                # May be inside of the if statement
                # if buffer size is == to 5
                s.sendto(header.encode(), addr)
                # if num_of_items_in_buffer == 7:
                #     write_to_file(num_of_items_in_buffer)
            s.settimeout(1)

        except timeout:
            # print("Timeout")
            write_to_file(num_of_items_in_buffer)
            #print("inside timeout")
            exit()

s.close()
