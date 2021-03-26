# ----- receiver.py -----

#!/usr/bin/env python
from collections import deque
from socket import *
import sys
import select
import json

host= '' #"0.0.0.0"
port = int(sys.argv[1])  #9999
s = socket(AF_INET,SOCK_DGRAM)
s.bind((host,port))

addr = (host,port)
buf=2800

f = open("received.txt",'wb')
data,addr = s.recvfrom(buf)

counter = 0

while True:
  try:
    data,addr = s.recvfrom(buf)
    data_json = json.loads(data)

    [(header, data)] = list(data_json.items())

    print("header we received is {}".format(header))
    print(type(header))

    if int(header) == counter:
        counter += 1
        print("send counter", counter)
        s.sendto(str(counter).encode(),addr)

    f.write(data.encode()) #send to app
    s.settimeout(10)

    if not data:
        break
  except timeout:
    print("time out")
    f.close()
    s.close()
    print("File Downloaded")