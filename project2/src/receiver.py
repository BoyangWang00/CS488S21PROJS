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
received_packets = []
timeout_counter = 0

while True:
    try:
        # Waiting for first packet from sender
        print("before recv")
        b_data, addr = s.recvfrom(s_buf)
        # deserialize json obj into python dict
        data_json = json.loads(b_data)
        [(header, data)] = list(data_json.items())
        index = int(header) % buffer_size
        # Put it inside of buffer_size
        # Check if we already received the packet but lost ACK
        if receiver_datagram_buffer.get(index) == '':
            if int(header) in received_packets:
                print("Resending ack ", int(header))
                s.sendto(header.encode(), addr)
            else:
                receiver_datagram_buffer[index] = data
                #print("inside else checking data", data)
                num_of_items_in_buffer += 1
                print("Sending ack ", int(header))
                received_packets.append(int(header))
                s.sendto(header.encode(), addr)

        # print(len(receiver_datagram_buffer))
        # WHY DOES THIS FAIL TASK 2
        print("# of items in buffer", num_of_items_in_buffer)
        if num_of_items_in_buffer > 3 and num_of_items_in_buffer < buffer_size:
            print("inside if items > 3")
            for i in range(buffer_size):
                print("data inside receiver buffer",
                      receiver_datagram_buffer.get(i))
                if receiver_datagram_buffer.get(i) != '':
                    print("try", i)
                    sys.stdout.write(receiver_datagram_buffer.get(i))
                    receiver_datagram_buffer[i] = ''
                    num_of_items_in_buffer -= 1
                else:
                    break
        print("before settimeout")
        s.settimeout(3)
    except timeout:
        print("inside timeout")

        for i in range(buffer_size):
            if receiver_datagram_buffer.get(i) != '':
                # print("timeout")
                sys.stdout.write(receiver_datagram_buffer.get(i))
                receiver_datagram_buffer[i] = ''
                s.sendto(header.encode(), addr)

            else:
                pass

        exit()


s.close()
