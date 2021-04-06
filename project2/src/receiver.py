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

buffer_size = 50
receiver_datagram_buffer = []
# Create an empty list
for i in range(buffer_size):
    receiver_datagram_buffer.append('')
num_of_items_in_buffer = 0
receiver_buffer_round_time = 1
received_packets = []
list_to_write = []
items_in_write = 0

DatagramInFlight = collections.namedtuple(
    'DatagramInFlight', ['header', 'data'])

# Sorts based off of key


def get_header(list_to_write):

    return list_to_write.header


# Retrieve the information about
while True:
    try:
        # print("Receiver: Inside True statement")
        # print("Receiver: Received Packets ", received_packets)
        # Get the packet with data
        b_data, addr = s.recvfrom(s_buf)
        # Deserialize so we can use it
        data_json = json.loads(b_data)
        [(header, data)] = list(data_json.items())
        index = int(header) % buffer_size
        # If the index is empty
        # if receiver_datagram_buffer[index] == '':
        if int(header) in received_packets:
            # Resending Ack because it's inside our list of packets received
            # print("Receiver: Sending Ack #", int(header), " again")
            s.sendto(str(header).encode(), addr)
            s.settimeout(2)
        elif receiver_datagram_buffer[index] == '' and int(header) != -1:
            # If it isn't the closeout header
            # if int(header) != -1:
            # Puts it into our Dict
            datagram_tuple = DatagramInFlight(header=int(header), data=data)
            # Insert in list with index
            receiver_datagram_buffer[index] = datagram_tuple
            num_of_items_in_buffer += 1
            # Add to list of packets already received
            received_packets.append(int(header))
            # Send Ack to Receiver
            s.sendto(str(header).encode(), addr)
            s.settimeout(2)
            # print("Receiver: Not timing out and sending Ack # ", int(header))
            # Writes immediately
            if num_of_items_in_buffer >= 4:
                # Loop through 0-20
                for i in range(buffer_size):
                    # If it isn't empty
                    if receiver_datagram_buffer[i] != '':
                        # Add whatever is in the buffer into our list to write to file
                        # Each receiver datagram is a tuple so we can use .data .header
                        # print("Receiver: inside of num > buffer")

                        list_to_write.append(
                            receiver_datagram_buffer[i])
                        # Empty the section once we append it to our list to write
                        receiver_datagram_buffer[i] = ''
                        # Decrease # of buffers/ For the threshold to empty our receiver buffer
                        num_of_items_in_buffer -= 1
                        items_in_write += 1

                        # print("Receiver: # of items in buffer when >4: ",num_of_items_in_buffer)

    except timeout:
        # print("Receiver: inside timeout")
        # print("Receiver: # of items in buffer: ", num_of_items_in_buffer)
        if (int(header) == -1 and num_of_items_in_buffer == 0):
            list_to_write.sort(key=get_header)
            #print("Receiver: inside close out/Writing out")
            for i in range(len(list_to_write)):
                # print("Receiver: Writing to file: ", list_to_write[i])
                # print("Receiver: The header we're writing is : ",list_to_write[i].header)
                sys.stdout.write(list_to_write[i].data)
            break
        # elif items_in_write > 100000:
        #     list_to_write.sort(key=get_header)
        #     for i in range(len(list_to_write)):
        #         #print("Receiver: Writing to file: ", list_to_write[i])
        #         sys.stdout.write(list_to_write[i].data)
        #         items_in_write -= 1

        elif num_of_items_in_buffer > 0:
            # print("inside else statement")
            for i in range(buffer_size):
                if receiver_datagram_buffer[i] != '':
                    datagram_tuple = receiver_datagram_buffer[i]
                    # #print(received_packets)
                    # print("Receiver: inside of timeout append")
                    # print("Receiver: Header # is ", datagram_tuple.header)

                    list_to_write.append(
                        receiver_datagram_buffer[i])
                    s.sendto(str(datagram_tuple.header).encode(), addr)
                    s.settimeout(2)
                    receiver_datagram_buffer[i] = ''
                    num_of_items_in_buffer -= 1
                    items_in_write += 1
                    # print("Receiver: # of items in buffer after timeout: ",num_of_items_in_buffer)


s.close()


# Put it inside a tuple and then inside a list

# Put the information into our own write to file buffer

# Send Ack to the sender saying we got the packet

# Once we timeout and there's nothing else to receive, then you quit
