# ---------sender.py--------

import collections
import socket
import sys
import time
import json
import errno

srtt = 0
srttdev = 0
timeout = 0

#     srtt[n] = alpha * rtt_sample + (1 - alpha) * srtt[n-1]
#     dev_sample = |rtt_sample - srtt[n]|
#     srttdev[n] = beta * dev_sample + (1 - beta) * srttdev[n-1]
#     timeout = srtt[n] + k * srttdev[n]
#     Assume: alpha = beta = 0.125 ; k=4


def srtt_cal(ack_receiving_time, packet_sent_out_time, srtt, srttdev):
    rtt_sample = ack_receiving_time - packet_sent_out_time
    if srtt == 0:
        timeout = rtt_sample
        srtt = rtt_sample
        srttdev = 0
    else:
        srtt = srtt * 0.875 + rtt_sample*0.125
        #print("srtt is ", srtt)
        dev_sample = abs(rtt_sample - srtt)
        #print("dev_sample is ", dev_sample)
        srttdev = 0.875 * srttdev + 0.125 * dev_sample
        #print("srttdev is ", srttdev)
        timeout = srtt + 4*srttdev
    return timeout, srtt, srttdev


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(0)
host = sys.argv[1]
port = int(sys.argv[2])
buf = 1400  # read from stdin
addr = (host, port)

# Setting up the deque and the information
total_data = 0
ack_data = 0
buffer_size = 20
sender_datagram_buffer = collections.deque(maxlen=buffer_size)
DatagramInFlight = collections.namedtuple(
    'DatagramInFlight', ['number', 'time', 'data'])
datagram_number = 0

# start time
start_time = time.time()

end_of_file = False
sender_packet_count = {}
receiver_closed = False

try:
    # try to read first batch of datagram from stdin
    for i in range(buffer_size):
        data = sys.stdin.read(buf)
        total_data += len(data)

        # serilize header and data
        b_data = json.dumps({datagram_number: data})

        s.sendto(b_data.encode(), addr)  # send regular packet
        sender_packet_count[datagram_number] = 1
        #print("{} bytes have been sent ...".format(total_data))

        datagram_tuple = DatagramInFlight(
            number=datagram_number, time=time.time(), data=b_data)
        sender_datagram_buffer.insert(i, datagram_tuple)
        datagram_number += 1
        #print("current data is type is ", type(data))
        if data == '':    # when we reach EOF we send out '' first and then break loop
            #print("Reach EOF")
            end_of_file = True
            break

except IOError:
    print("Sender: IOError")

# Define Packets in the beginning

while len(sender_datagram_buffer) > 0 and receiver_closed != True:
    try:
        # receive AKC
        ack_data, addr = s.recvfrom(100)
        # print("akc # is {}, datagram_number is {}".format(ack_data, datagram_number))

        ack_receiving_time = time.time()

        if ack_data.decode() == '-1':
            #print("receiver is closed")
            receiver_closed = True
            break
        else:

            for i in range(len(sender_datagram_buffer)):
                #print("i is ", i ,"buffer_size is ",len(sender_datagram_buffer))
                datagram_tuple = sender_datagram_buffer[i]

                if int(ack_data.decode()) == datagram_tuple.number:
                    # cal srtt for current ack
                    timeout, srtt, srttdev = srtt_cal(
                        ack_receiving_time, datagram_tuple.time, srtt, srttdev)
                    #print("srtt is", float(srtt)*1_000_000_000)

                    if end_of_file != True:
                        # if ack we received is for datagram in buffer and we haven't reach the EOF
                        # fetch new data and send it out
                        # replace old datagram with new one
                        data = sys.stdin.read(buf)
                        total_data += len(data)
                        sender_datagram_buffer.remove(datagram_tuple)
                        if data == '':
                            # After we send out the first empty string as a signal EOF
                            # turn on end_of_file flag
                            end_of_file = True
                            b_data = json.dumps({datagram_number: data})
                            # send regular packet
                            s.sendto(b_data.encode(), addr)
                            sender_packet_count[datagram_number] = 1
                        else:
                            # serilize header and data
                            b_data = json.dumps({datagram_number: data})
                            # send regular packet
                            s.sendto(b_data.encode(), addr)
                            sender_packet_count[datagram_number] = 1
                        datagram_tuple_new = DatagramInFlight(
                            number=datagram_number, time=time.time(), data=b_data)
                        sender_datagram_buffer.insert(i, datagram_tuple_new)
                        datagram_number += 1

                    else:
                        # we already reached EOF and already sent out '';
                        # thus only remove datagram from buffer
                        sender_datagram_buffer.remove(datagram_tuple)

                    # after taking care of ack break out loop.
                    break
                else:
                    # if ACK ! = datagram_tuple.number, check next datagram_tuple in buffer.
                    pass

    except socket.error as e:
        # Timedout

        if len(sender_datagram_buffer) > 0:

            for i in range(len(sender_datagram_buffer)):
                # print(len(sender_datagram_buffer))
                datagram_tuple = sender_datagram_buffer[i]
                if time.time() - datagram_tuple.time > timeout:
                    resend_time = time.time()
                    # serilize header and data
                    b_data = datagram_tuple.data
                    sender_datagram_buffer[i] = sender_datagram_buffer[i]._replace(
                        time=resend_time)
                    assert sender_datagram_buffer[i].time == resend_time
                    #print("resend b/c time out datagram number is", datagram_tuple.number)
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
    print("Sender: Sent {} bytes in {} seconds: {} kB/s".format(total_data,
                                                                round(time), round(speed)))

# Connection Handler


# Read Requested file


# Break it down and send it in multiples of your byte size


print("Sent {} bytes in {} seconds: {} kB/s".format(total_data,
                                                    round(time), round(speed)))
print("srtt is ", srtt)
exit()

# print(sender_packet_count)