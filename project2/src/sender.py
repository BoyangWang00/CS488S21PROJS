# ----- sender.py ------

#!/usr/bin/env python
from socket import *
import sys
import time
import json

s = socket(AF_INET, SOCK_DGRAM)
host = sys.argv[1]
port = int(sys.argv[2])
buf = 1400  # read from stdin
addr = (host, port)

# f=open("a.txt","rb")
total_data = 0

start_time = time.time()
header_index = 0
akc_data = 0

while True:
    try:
        data = sys.stdin.read(buf)
        #print("current data is",data, "type is ", type(data))
        #b_data = data.encode()
        b_data = json.dumps({header_index: data})

        # TODO: change the header index

    except IOError:
        print("IOError")

        # stop and wait the AKC for last packet
    if(s.sendto(b_data.encode(), addr)):  # send regular packet
        total_data += len(b_data)
        #print("{} bytes have been sent ...".format(total_data))
        try:


            if data == '':    # when we reach EOF
                print("Send finished")
                end_time = time.time()
                b_data = "-1"
                s.sendto(b_data.encode(), addr)
                break

            s.settimeout(2)
            # receive AKC
            akc_data, addr = s.recvfrom(100)

            #print("akc # is {}".format(akc_data))

            if int(akc_data) == header_index +1:
                header_index +=1
                continue
            else:
                #resned the packet
                s.sendto(b_data.encode(),addr)
                print("send again b/c packet lost")

        except timeout:

            # resend the packet
            s.sendto(b_data.encode(), addr)
            #print("send again b/c time out")

        if int(akc_data)== header_index + 1:
            #print("akc is ", int(akc_data))
            header_index += 1
            continue
        else:
            # resned the packet
            s.sendto(b_data.encode(), addr)
            #print("send again b/c packet lost")
    else:
        #print("failed to send data")
        break


time = (end_time - start_time)
if time == 0:
    speed = 0
    print("Input file is too small to measure")
else:
    speed = total_data/time/1000

print("Sent {} bytes in {} seconds: {} kB/s".format(total_data,
                                                    round(time), round(speed)))
s.close()
# f.close()
