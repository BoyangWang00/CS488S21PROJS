# ---- Project 2 Task 3 Experiment Code ----
# Dynamic EMWA
from socket import *
import sys
import os

 #varied alpha: 0.1 <= alpha <= 0.25
aMin = .1
aMax = .25
avgRate = 0
winSize = 5
#holding the past values in memory buffer and constantly updating the buffer whenever a new observation is read
srtt = [] #memory buffer of smoothed rtt's (timeout = srtt[n])

print("Testing window size {}".format(winSize))

#Measure rtt for each winSize, instead of measuring for each packet (overhead)
try:
    for i in range(winSize):
        num_packets = winSize
        num_packets/winSize

while len(sender_datagram_buffer) > 0: #maybe??? need to run while sender is sending datagram, for each one
  #find current rtt of datagram n
  n = datagram_tuple(0) #get datagram number

  #find current rtt of current datagram
  curr_rtt = (time of ack) - datagram_tuple(1)
  # need to implement variable to store time of sender receiving ack
  # re: datagram_tuple(1) = time datagram sent

  #find smooth rtt and add to srtt
  if len(srtt) < 1:
    # corner case, first datagram
    srtt[0] = (A * curr_rtt + (1 - A))
    # need to figure out starting value...
  else:
    #smooth rtt
    srtt[n] = (A * curr_rtt + (1 - A) * srtt[n-1])

#find mean
mean = srtt[] / n

# find median
median = srtt[n/2]

#find min, max
min, max = srtt[0]
for(i = 1 until n):
  if srtt[n] < min:
    min = srtt[n]
  if srtt[n] > max:
    max = srtt[n]

return min, max, median, mean
