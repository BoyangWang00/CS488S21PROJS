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
ack_data = 0
buffer_size = 500
sender_datagram_buffer = collections.deque(maxlen=buffer_size)
DatagramInFlight = collections.namedtuple('DatagramInFlight', ['number','time','data'])
datagram_number = 0

start_time = time.time()

end_of_file = False
sender_packet_count={}

try: 
# try to read first batch of datagram from stdin
    for i in range(buffer_size):
        data = sys.stdin.read(buf)
        total_data += len(data)
        
        #serilize header and data
        datagram_number += 1
        b_data = json.dumps({datagram_number: data})

        s.sendto(b_data.encode(), addr)  # send regular packet
        sender_packet_count[datagram_number] = 1
        #print("{} bytes have been sent ...".format(total_data))

        datagram_tuple = DatagramInFlight(number=datagram_number,time = time.time(), data = b_data)
        sender_datagram_buffer.insert(i,datagram_tuple)
        #print("current data is type is ", type(data))
        if data == '':    # when we reach EOF we send out '' first and then break loop
            #print("Reach EOF")
            end_of_file = True
            break

except IOError:
    print("IOError")

while len(sender_datagram_buffer) > 0:
    try:
        # receive AKC
        ack_data, addr = s.recvfrom(100)
        #print("akc # is {}, datagram_number is {}".format(ack_data, datagram_number))

        for i in range(len(sender_datagram_buffer)):
            #print("i is ", i ,"buffer_size is ",len(sender_datagram_buffer))
            datagram_tuple = sender_datagram_buffer[i]

            if int(ack_data.decode()) == datagram_tuple.number:
                if end_of_file != True:
                # if ack we received is for datagram in buffer and we haven't reach the EOF 
                # fetch new data and send it out 
                # replace old datagram with new one
                    data = sys.stdin.read(buf)
                    total_data += len(data)
                    sender_datagram_buffer.remove(datagram_tuple)
                    #serilize header and data
                    datagram_number += 1
                    b_data = json.dumps({datagram_number: data})
                    s.sendto(b_data.encode(), addr)  # send regular packet
                    sender_packet_count[datagram_number] = 1
                    datagram_tuple_new = DatagramInFlight(number=datagram_number,time = time.time(), data = b_data)
                    sender_datagram_buffer.insert(i,datagram_tuple_new)

                    if data == '':
                        #After we send out the first empty string as a signal EOF
                        #turn on end_of_file flag
                       end_of_file = True
                else:
                # we already reached EOF and already sent out ''; 
                # thus only remove datagram from buffer
                    sender_datagram_buffer.remove(datagram_tuple)

                #after taking care of ack break out loop.
                break
            else:
                #if ACK ! = datagram_tuple.number, check next datagram_tuple in buffer.
                pass

    except socket.error as e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            # no more ack received; check timeout and resend
            for i in range(len(sender_datagram_buffer)):
                datagram_tuple = sender_datagram_buffer[i]
                if time.time() - datagram_tuple.time > 0.01:
                        resend_time = time.time()
                        #serilize header and data
                        b_data = datagram_tuple.data
                        sender_datagram_buffer[i] = sender_datagram_buffer[i]._replace(time = resend_time)
                        assert sender_datagram_buffer[i].time == resend_time
                        #print("datagram number is", datagram_tuple.number)
                        # resend the packet
                        s.sendto(b_data.encode(), addr)
                        sender_packet_count[datagram_tuple.number] += 1
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
#print(sender_packet_count)