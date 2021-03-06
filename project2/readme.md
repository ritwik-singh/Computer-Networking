
# TCP

- We have designed a reliable streaming transport protocol on top of UDP. We have built a simplified version of TCP.
- Firstly, we built a streamer in which we chunked the data and sent them in multiple packets.
- Then we added reordering in the steamer by adding sequence numbers and a receive buffer.
- We implemented a stop and wait for the algorithm to solve the packet loss by adding acknowledgments, timeouts, and retransmissions.
- A protocol can suffer from corruption as well. We added a hash of a packet in the segment header and discarded any packets that failed the hash test to solve this problem.
- We implemented selective repeat by using threads and locks to allow in-flight packets to be reordered.
