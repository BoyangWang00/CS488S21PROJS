# ----- sender.py ------

#!/usr/bin/env python
from socket import *
import sys
import time

s = socket(AF_INET,SOCK_DGRAM)
host = sys.argv[1]
port = int(sys.argv[2])
buf = 1400   #read from stdin
addr = (host,port)

#f=open("a.txt","rb")
total_data = 0

start_time = time.time()
while True:
    try:
        data = sys.stdin.buffer.read(buf)
        #b_data = data.encode()
        b_data = data
    except IOError:
        print ("IOError")

        #stop and wait the AKC for last packet
    if(s.sendto(b_data,addr)): #send regular packet
        total_data += len(b_data)
        print("{} bytes have been sent ...".format(total_data))

    if len(b_data) < buf:    # the last read will be less than 1400; we jump out of the loop
        print("sending last packet...")
        end_time = time.time()
        break

time = (end_time - start_time)
if time == 0:
    speed = 0
    print("Input file is too small to measure")
else:
    speed = total_data/time/1000

print("Sent {} bytes in {} seconds: {} kB/s".format(total_data, time ,round(speed)))
s.close()
#f.close()
