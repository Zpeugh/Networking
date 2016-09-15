'''
    CSE 3461: Lab 2
    Author: Zach Peugh
    Date: 9/14/2016
    Description: Server script which opens a socket on the given
                 port then receives a file chunk by chunk,
                 writing that file to an output directory
'''

from socket import *
import sys
import os
import math


##############################   Global variables  ##############################
CHUNK_SIZE = 1000       # The size in bytes of chunks of file to receive at a time
HEADER_SIZE = 4         # The size in bytes of the file size integer
FILE_NAME_SIZE = 20     # The size in bytes of the file name string
SERVER_RESP_SIZE = 12   # The size in bytes of the server response
OUTPUT_DIR = "output/"


#################################   Functions   #################################

def open_socket(port_number):
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind(('',port_number))
    serverSocket.listen(1)
    print('The server is ready to receive')
    return serverSocket


def receive_file_size(serverSocket):
    connectionSocket, addr = serverSocket.accept()
    file_size_bytes = connectionSocket.recv(HEADER_SIZE)
    file_size = int.from_bytes(file_size_bytes, byteorder="little")
    print("Expected file length: {0}".format(file_size))
    connectionSocket.send("success".encode(encoding="ascii"))
    return file_size


def receive_file_name(serverSocket):
    connectionSocket, addr = serverSocket.accept()
    file_name_bytes = connectionSocket.recv(FILE_NAME_SIZE)
    file_name = file_name_bytes.decode(encoding="ascii")
    print("File name: {0}".format(file_name))
    connectionSocket.send("success".encode(encoding="ascii"))
    return file_name.strip()


def receive_file(serverSocket,file_size):
    chunk_num = 1       # Initialize a counter for screen output
    byte_array = b""    # Initialize a byte to append the file data stream to
    EOF = "".encode(encoding="ascii")   # arbitrarily chosen end of file marker

    while True:
        connectionSocket, addr = serverSocket.accept()
        data = connectionSocket.recv(CHUNK_SIZE)
        connectionSocket.send("success".encode(encoding="ascii"))

        if data == EOF:
            print("Finished receiving file, closing socket")
            connectionSocket.close()
            return byte_array
        else:
            byte_array += data
            print("{0}/{1} chunks received".format(chunk_num, math.ceil(file_size/CHUNK_SIZE)))
            chunk_num += 1

def write_file(file_name, file_data):
    # check if the output directory exists, create it if it does not
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    out_file = open(OUTPUT_DIR + file_name, 'wb')
    out_file.write(file_data)
    out_file.close()


###############################   Script Execution   ###############################

port_number = int(sys.argv[1])              # Get port number from commandline

serverSocket = open_socket(port_number)

file_size = receive_file_size(serverSocket)
file_name = receive_file_name(serverSocket)
file_bytes = receive_file(serverSocket, file_size)
write_file(file_name, file_bytes)
