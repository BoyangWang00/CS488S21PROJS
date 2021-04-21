
# ----- receiver.py -----
# ----- StopAndWait task2 -----

#!/usr/bin/env python

from socket import *
import sys
import select
import base64
import json


host = "0.0.0.0"
port = int(sys.argv[1])
s = socket(AF_INET, SOCK_DGRAM)
s.bind((host, port))
addr = (host, port)
buf = 2800
seqNum = 0

#print('Receiving first datagram')
datagram, addr = s.recvfrom(buf)  # first recieved datagram
ackment = 0

# Credit: https://stackoverflow.com/questions/55277431/python-convert-dictionary-to-bytes$
msg_bytes = base64.b64decode(datagram)
ascii_message = msg_bytes.decode('ascii')
asc_message = ascii_message.replace("'", "\"")
dict_pair = json.loads(asc_message)


while(datagram):
    try:
        keys_list = list(dict_pair)
        key = keys_list[0]
        strSeqNum = str(seqNum)
#      temp_key = int(key)+1
        msg_bytes = base64.b64decode(datagram)
        ascii_message = msg_bytes.decode('ascii')
        asc_message = ascii_message.replace("'", "\"")
        dict_pair = json.loads(asc_message)

        if (key == strSeqNum):
            #print('This is the expected chunk of data with seqNum {}'.format(key))
            #print('Sending ACK {}'.format(ackment))
            # sends ACK for expected SEQ
            sentACK = s.sendto(ackment.to_bytes(5, byteorder='big'), addr)
#         print('Incrementing both ackment and seqNum')
            ackment = ackment+1
            seqNum = seqNum+1
            temp_ack = ackment
            datagram, addr = s.recvfrom(buf)
            s.settimeout(3)

        else:  # this is the repeating data (I got it before)
            #         print('I assume my previous ACK {} got lost'.format(temp_ack))
            #         print('So sender resent the datagram')
            #         print('I am resending the ACK for datagram with seqNum {}'.format(temp_ack))
            #sentACK = s.sendto(temp_ack.to_bytes(5, byteorder='big'), addr)

    except timeout:
        s.close()
