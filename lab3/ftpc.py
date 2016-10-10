'''
    CSE 3461: Lab 2
    Author: Zach Peugh
    Date: 9/14/2016
    Description: Client script which connects to a socket of a
                 given host on a specific port, and then transfers
                 the file to the server directory.
'''



from socket import *
import sys
import os

CHUNK_SIZE = 1000       # The size in bytes of chunks of file to receive at a time
HEADER_SIZE = 4         # The size in bytes of the file size integer
FILE_NAME_SIZE = 20     # The size in bytes of the file name string
SERVER_RESP_SIZE = 12   # The size in bytes of the server response
OUTPUT_DIR = "output/"


def initialize_socket():
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((hostIP,portNumber))
    return client_socket


def send_file_size(file_name):
    client_socket = initialize_socket()
    file_size = os.path.getsize(file_name);
    file_size_bytes = (file_size).to_bytes(HEADER_SIZE,byteorder="little")
    client_socket.send(file_size_bytes)
    result = client_socket.recv(SERVER_RESP_SIZE)
    print("File size response: {0}".format(result.decode(encoding="ascii")))
    client_socket.close()

def send_file_name(file_name):
    client_socket = initialize_socket()
    correct_size_file_name = file_name.ljust(FILE_NAME_SIZE)
    file_name_bytes = correct_size_file_name.encode(encoding="ascii")
    client_socket.send(file_name_bytes)
    result = client_socket.recv(SERVER_RESP_SIZE)
    print("File name response: {0}".format(result.decode(encoding="ascii")))
    client_socket.close()

def send_file(file_name):
    chunk_num = 1
    with open(file_name, 'rb') as f:
        data = f.read(CHUNK_SIZE)
        while data:
            client_socket = initialize_socket()
            client_socket.send(data)
            result = client_socket.recv(SERVER_RESP_SIZE)
            client_socket.close()
            print("File chunk {0}: {1}".format(chunk_num, result.decode(encoding="ascii")))
            chunk_num += 1
            data = f.read(CHUNK_SIZE)

    client_socket = initialize_socket()
    client_socket.send("".encode(encoding="ascii"))
    client_socket.close()
    print("Successfully transferred file")


############################## Begin script execution ##############################


# Get the input arguments from the commandline call
hostIP = sys.argv[1]        # Server IP address
portNumber = int(sys.argv[2])    # Server port number
file_name = sys.argv[3]      # Relative path to the file to send

send_file_size(file_name)
send_file_name(file_name)
send_file(file_name)
