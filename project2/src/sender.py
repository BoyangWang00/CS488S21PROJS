# ----- sender.py ------

#!/usr/bin/env python
import collections
import socket
import sys
import time
import json
import errno

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(False)
host = sys.argv[1]
port = int(sys.argv[2])
buf = 1400  # read from stdin
addr = (host, port)

total_data = 0
akc_data = 0
buffer_size = 5
sender_datagram_buffer = collections.deque(maxlen=buffer_size)
DatagramInFlight = collections.namedtuple('DatagramInFlight', ['number','time','data'])
datagram_number = 0

start_time = time.time()
try:
    for i in range(buffer_size):
        data = sys.stdin.read(buf)
        total_data += len(data)
        
        #serilize header and data
        datagram_number += 1
        b_data = json.dumps({datagram_number: data})

        s.sendto(b_data.encode(), addr)  # send regular packet
        #print("{} bytes have been sent ...".format(total_data))

        datagram_tuple = DatagramInFlight(number=datagram_number,time = time.time(), data = b_data)
        sender_datagram_buffer.insert(i,datagram_tuple)
        #print("current data is type is ", type(data))
        if data == '':    # when we reach EOF
            print("Reach EOF")
            break

except IOError:
    print("IOError")

while len(sender_datagram_buffer) > 0:
    try:
        # receive AKC
        akc_data, addr = s.recvfrom(100)
        print("akc # is {}, datagram_number is {}".format(akc_data, datagram_number))

        for i in range(len(sender_datagram_buffer)):
            print("i is ", i ,"buffer_size is ",len(sender_datagram_buffer))
            datagram_tuple = sender_datagram_buffer[i]

            if int(akc_data.decode()) == datagram_tuple.number:
                data = sys.stdin.read(buf)
                total_data += len(data)
                if data == '':
                    sender_datagram_buffer.remove(datagram_tuple)
                    #if len(sender_datagram_buffer) == 0:
                    break
                else:
                    #serilize header and data
                    datagram_number += 1
                    b_data = json.dumps({datagram_number: data})
                    s.sendto(b_data.encode(), addr)  # send regular packet
                    datagram_tuple_new = DatagramInFlight(number=datagram_number,time = time.time(), data = b_data)
                    sender_datagram_buffer.remove(datagram_tuple)
                    sender_datagram_buffer.insert(i,datagram_tuple_new)
            else:
                pass

    except socket.error as e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            # no more ack received; check timeout and resend
            for i in range(len(sender_datagram_buffer)):
                datagram_tuple = sender_datagram_buffer[i]
                if time.time() - datagram_tuple.time > 2:
                        #serilize header and data
                        b_data = json.dumps({datagram_tuple.number: datagram_tuple.data})
                        # resend the packet
                        s.sendto(b_data.encode(), addr)
                        #print("send again b/c time out")

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
