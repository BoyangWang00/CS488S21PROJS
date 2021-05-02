# ---- Project 2 Task 3 Experiment Code ----
# Implenting EMWA: holding the past values in memory buffer and constantly updating the buffer whenever a new observation is read

# to fix:
# set custom window size parameter for test - this meant to go here?
# is the while loop condition correct? 0_0
# test starter value in if statement

import collections
import socket

A = .1 #varied alpha: 0.1 <= alpha <= 0.25
srtt = [] #memory buffer of smoothed rtt's (timeout = srtt[n])
srtt.append() = 0

# need to implement set window size parameter in sender
# winSize =
# print("Testing window size {0}".format(winSize))

#how to measure rtt of each datagram while socket is sending/receiving?...
#while len(sender_datagram_buffer) > 0:
while s.sendto(b_data.encode(), addr) != 0:
  #find current rtt of datagram n
  n = datagram_tuple(0) #get datagram number

  #find current rtt of current datagram
  curr_rtt = akc_time - datagram_tuple(1)
  # need to implement variable to store time of sender receiving ack
  # re: datagram_tuple(1) = time datagram sent

  #add curr_rtt to srtt buffer
  srtt.insert(n, curr_rtt)

  #--ignore for now--
  #if len(srtt) < 1:
    # corner case, first datagram
    # not sure if this is starter value
    #srtt[0] = (A * curr_rtt + (1 - A))
    # need to figure out starting value...
  #else:
    #smooth rtt
    #srtt[n] = (A * curr_rtt + (1 - A) * srtt[n-1])
   #---------------

#end of while loop, socket finished sending. Now:
# n = index of last datagram sent/acked
n = len(srtt) - 1
#so srtt[n] is the last datagram and srtt[n-1] is the previous datagram sent before it
# next, find mean (EMWA):
mean = A * srtt[n] + (1-A) * srtt[n-1]

# find median
median = srtt[int(n/2)]

#find min, max
min, max = srtt[0]
for(i = 1 until n):
  if srtt[n] < min:
    min = srtt[n]
  if srtt[n] > max:
    max = srtt[n]

print("Test done! \n Median = {0} \n Mean = {1} \n Min = {2} \n Max = {3}".format(median, mean, min, max))
