# ---- Project 2 Task 3 Experiment Code ----
# Implenting EMWA: holding the past values in memory buffer and constantly updating the buffer whenever a new observation is read

A = .1 #varied alpha: 0.1 <= alpha <= 0.25
srtt = [] #memory buffer of smoothed rtt's (timeout = srtt[n])


# need to implement set window size parameter in sender
# winSize =
print("Testing window size {0}".format(winSize))

#how to measure rtt of each datagram while socket is sending/receiving?...
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
