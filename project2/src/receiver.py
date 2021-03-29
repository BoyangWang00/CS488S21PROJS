# ----- receiver.py -----

#!/usr/bin/env python
from collections import deque
from socket import *
import sys
import select
import json

host = ''  # "0.0.0.0"
port = int(sys.argv[1])  # 9999
s = socket(AF_INET, SOCK_DGRAM)
s.bind((host, port))

addr = (host, port)
buf = 2800

counter = 0

while True:
    try:
        data, addr = s.recvfrom(buf)  # Waiting for first packet from sender
        data_json = json.loads(data)  # deserialize json obj into python dict

        [(header, data)] = list(data_json.items())

        #print("header wereceived is {}".format(header))
        #print(type(header))

        if int(header) == counter:
            counter += 1
            #print("send counter", counter)
            s.sendto(str(counter).encode(), addr)

        #f.write(data.encode())  # send to app
        sys.stdout.write(data)
        s.settimeout(2)

        if not data:
            break
    except timeout:
        #print("time out")
        exit(2)
s.close()
