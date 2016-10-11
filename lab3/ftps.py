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
IP_SIZE = 4                     # The size in bytes of the IP server host name
PORT_SIZE = 2                   # The size in bytes of the server port number
FLAG_SIZE = 1                   # The size in bytes of the flag
CHUNK_SIZE = 1000               # The size in bytes of chunks of file to receive at a time
SERVER_RESP_SIZE = CHUNK_SIZE   # The size in bytes of the server resposne
OUTPUT_DIR = "output/"          # The directory to store received files.
DGRAM_SIZE = IP_SIZE + PORT_SIZE + FLAG_SIZE + CHUNK_SIZE

#################################   Functions   #################################

def parse_datagram(payload):
    cli_ip = payload[0:IP_SIZE].decode(encoding="ascii")
    cli_port = int.from_bytes(payload[IP_SIZE:IP_SIZE+PORT_SIZE], byteorder="little")
    cli_flag = int.from_bytes(payload[IP_SIZE+PORT_SIZE:IP_SIZE+PORT_SIZE+FLAG_SIZE], byteorder="little")
    #print("\n\n############ NEXT SEGMENT ###########")
    #print("client ip:", cli_ip)
    #print("client port:", cli_port)
    #print("client flag:", cli_flag)
    data = payload[IP_SIZE+PORT_SIZE+FLAG_SIZE:]
    return cli_ip, cli_port, cli_flag, data


###############################   Script Execution   ###############################

port_number = int(sys.argv[1])              # Get port number from commandline
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.bind(('',port_number))

print("Waiting for UPD packets")
file_name = ""
out_file = ""
file_size = 1
bytes_received = 0

while True:
    payload, addr = clientSocket.recvfrom(DGRAM_SIZE)
    ip, port, flag, data = parse_datagram(payload)

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
    else:
        print("ERROR: Invalid flag")

    clientSocket.sendto(payload, addr)

out_file.close()
clientSocket.close()
