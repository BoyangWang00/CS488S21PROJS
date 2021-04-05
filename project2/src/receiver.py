# -----receiver.py-------

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
receiver_datagram_buffer = []
# Create an empty list
for i in range(buffer_size):
    receiver_datagram_buffer.append('')
num_of_items_in_buffer = 0
receiver_buffer_round_time = 1
received_packets = []
packet_counter = 0
next_packet = 1

DatagramInFlight = collections.namedtuple(
    'DatagramInFlight', ['header', 'data'])

# Retrieve the information about
while True:
    try:
        # Get the packet with data
        b_data, addr = s.recvfrom(s_buf)
        # Deserialize so we can use it
        data_json = json.loads(b_data)
        [(header, data)] = list(data_json.items())
        index = int(header) % buffer_size

        if receiver_datagram_buffer[index] == '':
            if int(header) in received_packets:
                # Resending Ack
                s.sendto(header.encode(), addr)
                s.settimeout(2)
            else:
                datagram_tuple = DatagramInFlight(header=header, data=data)
                receiver_datagram_buffer.insert(index, datagram_tuple)
                num_of_items_in_buffer += 1
                received_packets.append(int(header))
                s.sendto(header.encode(), addr)
                s.settimeout(2)
                # Writes immediately
                if num_of_items_in_buffer > 15 and num_of_items_in_buffer < buffer_size:
                    for i in range(buffer_size):
                        if receiver_datagram_buffer[i] != '' and (packet_counter+1) == next_packet:
                            sys.stdout.write(receiver_datagram_buffer[i].data)
                            receiver_datagram_buffer[i] = ''
                            num_of_items_in_buffer -= 1
                            packet_counter += 1
                            next_packet += 1

    except timeout:
        if int(header) == -1:
            break
        next_packet = 1
        packet_counter = 0
        for i in range(buffer_size):
            if int(header) in received_packets and receiver_datagram_buffer[i] != '' and packet_counter + 1 == next_packet:

                # print("timeout")
                sys.stdout.write(receiver_datagram_buffer[i].data)
                receiver_datagram_buffer[i] = ''
                s.sendto(header.encode(), addr)
                s.settimeout(2)
                num_of_items_in_buffer -= 1
                packet_counter += 1
                next_packet += 1

# Put it inside a tuple and then inside a list

# Put the information into our own write to file buffer

# Send Ack to the sender saying we got the packet

# Once we timeout and there's nothing else to receive, then you quit
