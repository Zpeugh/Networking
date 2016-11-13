'''
    CSE 3461: Lab 3
    Author: Zach Peugh
    Date: 10/10/2016
    Description: Server script which opens a UPD socket on the
                 given port then receives a file chunk by chunk,
                 writing that file to an output directory.
'''

import socket
import sys
import os
import math

##############################   Global variables  ##############################
FIRST_SEG_SIZE = 4              # The size in bytes of the file size integer
SECOND_SEG_SIZE = 20            # The size in bytes of the file name string
IP_SIZE = 10                     # The size in bytes of the IP server host name
PORT_SIZE = 2                   # The size in bytes of the server port number
FLAG_SIZE = 1                   # The size in bytes of the flag
SEQ_NUM_SIZE = 1                # The size in bytes of the sequence number
CHUNK_SIZE = 1000               # The size in bytes of chunks of file to receive at a time
SERVER_RESP_SIZE = CHUNK_SIZE   # The size in bytes of the server resposne
OUTPUT_DIR = "output/"          # The directory to store received files.
DGRAM_SIZE = IP_SIZE + PORT_SIZE + FLAG_SIZE + SEQ_NUM_SIZE + CHUNK_SIZE

#################################   Functions   #################################

def parse_datagram(payload):
    cli_ip = payload[:IP_SIZE].decode(encoding="ascii")
    cli_port = int.from_bytes(payload[IP_SIZE:IP_SIZE+PORT_SIZE], byteorder="little")
    cli_flag = int.from_bytes(payload[IP_SIZE+PORT_SIZE:IP_SIZE+PORT_SIZE+FLAG_SIZE], byteorder="little")
    cli_seq_num = int.from_bytes(payload[IP_SIZE+PORT_SIZE+FLAG_SIZE:IP_SIZE+PORT_SIZE+FLAG_SIZE+SEQ_NUM_SIZE], byteorder="little")

    print("\n\n############ NEXT SEGMENT ###########")
    print("client ip:", cli_ip)
    print("client port:", cli_port)
    print("client flag:", cli_flag)
    print("client seq:", cli_seq_num)

    data = payload[IP_SIZE+PORT_SIZE+FLAG_SIZE+SEQ_NUM_SIZE:]
    return cli_ip, cli_port, cli_flag, cli_seq_num, data

def ack(num):
    return (num).to_bytes(SEQ_NUM_SIZE,byteorder="little")

###############################   Script Execution   ###############################

port_number = int(sys.argv[1])              # Get port number from commandline
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.bind(('',port_number))

print("Waiting for UPD packets")
file_name = ""
out_file = ""
file_size = 1
bytes_received = 0
expected_seq_num = 0

while True:
    payload, addr = clientSocket.recvfrom(DGRAM_SIZE)
    ip, port, flag, seq_num, data = parse_datagram(payload)
    if seq_num == expected_seq_num:
        print("got seq_num {0}".format(seq_num))
        if flag == 1:
            file_size = int.from_bytes(data, byteorder="little")
            print("File size:", file_size)

        elif flag == 2:
            file_name = data.decode(encoding="ascii").strip()
            if not os.path.exists(OUTPUT_DIR):
                os.mkdir(OUTPUT_DIR)
            print("Creating file: ", file_name)
            out_file = open(OUTPUT_DIR + file_name, 'wb')

        elif flag == 3:
            if out_file != "" and file_size != 0:
                bytes_received += sys.getsizeof(data)
                print("{0}/{1} bytes received".format(bytes_received,file_size))
                out_file.write(data)
        elif flag == 4:
            if out_file != "" and file_size != 0:
                print("File transfer finished, closing connection")
                out_file.close()
                clientSocket.sendto(ack(expected_seq_num), addr)
                break;
        else:
            print("ERROR: Invalid flag")
        # send ACK
        clientSocket.sendto(ack(expected_seq_num), addr)
        expected_seq_num = int(expected_seq_num == False)
    else:
        # send NACK
        clientSocket.sendto(ack(int(expected_seq_num == False)), addr)
        print("recieved duplicate data")

clientSocket.close()
