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
last_buffer_size = buffer_size
# receiver_datagram_buffer = collections.deque(maxlen=buffer_size)
receiver_datagram_buffer = {}
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


end_of_file = False

    return list_to_write.header


# Retrieve the information about
while True:
        # print(len(receiver_datagram_buffer))
        if num_of_items_in_buffer < buffer_size and num_of_items_in_buffer < last_buffer_size:
            try:
                # Waiting for first packet from sender
                b_data, addr = s.recvfrom(s_buf)
                # deserialize json obj into python dict
                data_json = json.loads(b_data)

                [(header, data)] = list(data_json.items())
                # print("header recevied is ", header)
                # print("receiver_buffer_round ", receiver_buffer_round_time)
                # print("last buffer_size", last_buffer_size, "num_of_items_in_buffer", num_of_items_in_buffer)

                if int(header) < (receiver_buffer_round_time-1)*buffer_size:
                # if we received a packet that we already write out
                # send out ack immediantly
                    s.sendto(header.encode(), addr)
                    # print("send ack ", header, "without put in buffer")

                elif((receiver_buffer_round_time-1)*buffer_size <= int(header) < receiver_buffer_round_time*buffer_size):
                    # print("insert", header)
                    s.sendto(header.encode(), addr)
                    position = int(header) % buffer_size
                    if receiver_datagram_buffer.get(position) == '':
                        num_of_items_in_buffer += 1
                        receiver_datagram_buffer[position] = data
                        # print("send ack ", header,"after adding to buffer")

                    if data == '':
                        # print('                   reach end_of_file')
                        end_of_file = True
                        last_buffer_size = int(header) % buffer_size+1
                        last_header = header

                else:
                    pass
                    # do nothing
                s.settimeout(5)

            except timeout:
                i = 0
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
                        num_of_items_in_buffer -= 1
                    # print("shoudln't end up here!!!time out!!!!!!!!!!!")
                s.close()
                exit(0)

    except timeout:
        # print("Receiver: inside timeout")
        # print("Receiver: # of items in buffer: ", num_of_items_in_buffer)
        if (int(header) == -1 and num_of_items_in_buffer == 0):
            list_to_write.sort(key=get_header)
            # print("Receiver: inside close out/Writing out")
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
                # print("buffer_size ", buffer_size, "last_buffer_size", last_buffer_size)
                # print("line 68")
                # print("-----------------write", i)
                if receiver_datagram_buffer.get(i) != '':
                    sys.stdout.write(receiver_datagram_buffer.get(i))
                    # print("write out buffer ", i)
                    receiver_datagram_buffer[i] = ''
                    num_of_items_in_buffer -=1
                    if end_of_file == True:
                        # print("this is last print")
                        for i in range(10):
                            s.sendto("-1".encode(), addr)
                            # print("resend last ack", -1)
                    # for h in range((receiver_buffer_round_time-1)*buffer_size,receiver_buffer_round_time*buffer_size):
                    #     s.sendto(str(h).encode(), addr)
                else:
                    # print(list(receiver_datagram_buffer.keys()))
                    # print("i is",i)
                    # print("BUG!!!!!!!! BUFFER IS NOT FULL")
                    break

            receiver_buffer_round_time += 1
            # print("receiver_buffer_round_time increment", receiver_buffer_round_time)
            # s.sendto(header.encode(), addr)

s.close()
exit(0)

