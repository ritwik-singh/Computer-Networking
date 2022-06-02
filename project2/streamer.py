

'''
Networking project 2
RELIABLE NETWORK TRANSPORT
Project created by Rutuja Kajave(net id rpk9907) and Ritwik Kumar Singh(net id rks6667)

'''

#import the required libraries

from threading import Timer
from lossy_socket import LossyUDP
from socket import INADDR_ANY
import struct
import time
from concurrent.futures import ThreadPoolExecutor
import hashlib

class Packet:

    '''

    We have created a class packet that we will use to create tcp packet 
    and will store attribbutes and headers like sequence number, flag
    data and checksum.

    flag -- lets us know that what type of packet it is depending on its value.
    value 0 -- regular packet.
    value 1 -- its an acknowledgement packet.
    value 2 -- its a fin packet.

    We choose to use only one flag rather than using 2 bool values so that we could
    decrease our header length. 
    we started with around 26 bytes and we were able to make it to 19 bytes

    '''

    def __init__(self, sequence_number=None, flag=None, data=None,checksum=None):
        self.packet_sequence_number = sequence_number
        self.flag = flag
        self.data = data
        self.checksum = checksum





class Streamer:

    def __init__(self, dst_ip, dst_port,
                 src_ip=INADDR_ANY, src_port=0):
        """Default values listen on all network interfaces, chooses a random source port,
           and does not introduce any simulated packet loss."""
        self.socket = LossyUDP()
        self.socket.bind((src_ip, src_port))
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.closed = False
        
        # keep records of the sequenc number depending of receiver or sender it acts there own seq number.
        self.sequence_number = 0
        #buffer to keep recieving packets
        self.receiving_buffer = {}
        #buffer to keep send packets
        self.send_buffer = {}
        #dict to keep track of acks
        self.ack = {}

        self.thread = ThreadPoolExecutor(max_workers=1)
        self.thread.submit(self.listener)

        
        

    def send(self, data_bytes: bytes) -> None:
        
        #pacet size of each chunks if we get some large data.
        packet_size = 1024
        

        for i in range(0,len(data_bytes),packet_size):
            
            # chunking the data using simple for loop
            data = data_bytes[i:i+packet_size] 

            # creating packet and its checksum and storing them togather back into packet
            packet = struct.pack('hb'+str(len(data))+'s',self.sequence_number,0,data)
            checksum = hashlib.md5(packet).digest()
            packet = checksum + packet
            self.ack[self.sequence_number] = False
            self.send_buffer[self.sequence_number] = packet            
            self.firstime(self.sequence_number)
            self.sequence_number += 1
            
    
    def firstime(self,number):

        """
        Its a timer that we have created that will retransmit the packet unitl we
        dont get its acks in every 0.9 seconds. using timer.
        """

        timer = Timer(0.9,self.firstime,[number])
        if not self.ack[number]:
            self.socket.sendto(self.send_buffer[number], (self.dst_ip, self.dst_port))
            timer.start()

    def recv(self) -> bytes:
        
        while (self.sequence_number not in self.receiving_buffer):
                time.sleep(0.01)
            
        curr_packet = self.receiving_buffer.pop(self.sequence_number)
        self.sequence_number += 1
        return curr_packet


    def listener(self):

        while not self.closed:
            try:
                data, _ = self.socket.recvfrom()
                if data:
                    #unpacking the packet
                    tmp_check_sum,tmp_seq_number,tmp_flag, tmp_data_bytes = struct.unpack('16shb'+str(len(data) - 19)+'s',data)
                    #creating the tcp packet using the upack data
                    tcp_packet = Packet(tmp_seq_number,tmp_flag,tmp_data_bytes,tmp_check_sum)
                    #calculating the new checksum so that we can check if data is right or not
                    tmp_check = hashlib.md5(data[16:]).digest()
                    #check weather the checksum is right or not for data corruption.
                    if tmp_check == tcp_packet.checksum:

                        #check if its ack packet.
                        if tcp_packet.flag == 1:
                            self.ack[tcp_packet.packet_sequence_number] = True

                        #check if its fin packet.
                        elif tcp_packet.flag == 2:
                            
                            #if its a fin packet send its ack back by creating a packet
                            res = struct.pack('hb'+str(len(b''))+'s',tcp_packet.packet_sequence_number,1,b'')
                            checksum = hashlib.md5(res).digest()
                            res = checksum + res
                            
                            self.socket.sendto(res,(self.dst_ip,self.dst_port))
                            
                        else:
                            
                            #if its a normal packet send its ack back by creating a packet
                            res = struct.pack('hb'+str(len(b''))+'s',tcp_packet.packet_sequence_number,1,b'')
                            checksum = hashlib.md5(res).digest()
                            res = checksum + res
                            self.socket.sendto(res,(self.dst_ip,self.dst_port))
                            self.receiving_buffer[tcp_packet.packet_sequence_number] = tcp_packet.data 

            except Exception as e:
                print("listener died")
                print(e)

    

    def close(self) -> None:
       

        '''
        Created a fin packet and send it and we are sending it until we receive its 
        ack and then go to sleep.
        '''
        fin_seq = self.sequence_number
        data = b''
        fin_res = struct.pack('hb'+str(len(data))+'s',fin_seq,2,data)
        checksum = hashlib.md5(fin_res).digest()
        fin_res = checksum + fin_res
        self.ack[fin_seq] = False
        
        while not self.ack[fin_seq]:
            self.socket.sendto(fin_res,(self.dst_ip,self.dst_port))
            time.sleep(0.5)
        
        time.sleep(5)

        self.closed = True
        self.socket.stoprecv()


