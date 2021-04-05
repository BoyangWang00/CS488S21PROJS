# ---------sender.py--------

import collections
import socket
import sys
import time
import json
import errno

# Binding socket and set blocking
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(0)
host = sys.argv[1]
port = int(sys.argv[2])
buf = 1400  # read from stdin
addr = (host, port)

# Setting up the deque and the information
total_data = 0
akc_data = 0
buffer_size = 5
sender_datagram_buffer = collections.deque(maxlen=buffer_size)
DatagramInFlight = collections.namedtuple(
    'DatagramInFlight', ['number', 'time', 'data'])
datagram_number = 0

# start time
start_time = time.time()
try:
    for i in range(buffer_size):
        data = sys.stdin.read(buf)
        total_data += len(data)

        # serilize header and data
        b_data = json.dumps({datagram_number: data})

        s.sendto(b_data.encode(), addr)  # send regular packet
        # print("{} bytes have been sent ...".format(total_data))
        datagram_tuple = DatagramInFlight(
            number=datagram_number, time=time.time(), data=b_data)
        sender_datagram_buffer.insert(i, datagram_tuple)
        datagram_number += 1
        # print("current data is type is ", b_data)
        if data == '':    # when we reach EOF
            print("Reach EOF")
            break

except IOError:
    print("IOError")

# Define Packets in the beginning

# Going through our tuple list to see what needs to be sent + removed
while True:
    # Beginning
    try:
        # Receive Ack
        akc_data, addr = s.recvfrom(100)
        # If we get Ack then remove and move on
        for i in range(len(sender_datagram_buffer)):
            datagram_tuple = sender_datagram_buffer[i]
            print("The packet # is", datagram_tuple.number)
            #This prints packet #
            # print(sender_datagram_buffer[i].number)
            if int(akc_data.decode()) == datagram_tuple.number:
                #Print Ack #
                print("The acknowledgement # is ", int(akc_data.decode()))
                try:
                    # Read again
                    data = sys.stdin.read(buf)
                    # Keep track of total read
                    total_data += len(data)
                    sender_datagram_buffer.remove(datagram_tuple)
                except IOError:
                    print("Nothing left to read")
                # If there's no data
                if data == '':
                    print("Not fetching more data, do nothing")
                    pass
                else:
                    print("Fetching more data")
                    # serilize header and data
                    datagram_number += 1
                    b_data = json.dumps({datagram_number: data})
                    s.sendto(b_data.encode(), addr)  # send regular packet
                    s.settimeout(2)
                    datagram_tuple_new = DatagramInFlight(
                        number=datagram_number, time=time.time(), data=b_data)
                    sender_datagram_buffer.insert(i, datagram_tuple_new)
                # Completed iterations through buffer
                break

    except socket.error as e:
        # Timedout

        if len(sender_datagram_buffer) == 0:
            b_data = json.dumps({-1: "-1"})
            s.sendto(b_data.encode(), addr)
            s.settimeout(2)
            break
        else:
            for i in range(len(sender_datagram_buffer)):
                datagram_tuple = sender_datagram_buffer[i]
                if time.time() - datagram_tuple.time > 1:
                    # serilize header and data
                    b_data = datagram_tuple.data
                    print("datagram number is", datagram_tuple.number)
                    # resend the packet
                    s.sendto(b_data.encode(), addr)
                    # print("send again b/c time out")
    # Go through the rest of the slider buffer to see which ACKs are needed and to re-send
s.close()
end_time = time.time()
time = (end_time - start_time)
if time == 0:
    speed = 0
    print("Input file is too small to measure")
else:
    speed = total_data/time/1000
    print("Sent {} bytes in {} seconds: {} kB/s".format(total_data,
                                                        round(time), round(speed)))

# Connection Handler


# Read Requested file


# Break it down and send it in multiples of your byte size


# Connection Initiation
