'''
    CSE 3461: Lab 3
    Author: Zach Peugh
    Date: 10/10/2016
    Description: Client script which connects to a socket of a
                 given host on a specific port, and then transfers
                 the file via UPD protocol through troll to the
                 server directory.
'''

import socket
import sys
import os
import time

FIRST_SEG_SIZE = 4      # The size in bytes of the file size integer
SECOND_SEG_SIZE = 20    # The size in bytes of the file name string
IP_SIZE = 4             # The size in bytes of the IP server host name
PORT_SIZE = 2           # The size in bytes of the server port number
FLAG_SIZE = 1           # The size in bytes of the flag
CHUNK_SIZE = 1000       # The size in bytes of chunks of file to receive at a time
CLIENT_PORT = 1567      # Arbitrarily chosen client port number to bind to
SERVER_RESP_SIZE = CHUNK_SIZE
DGRAM_SIZE = IP_SIZE + PORT_SIZE + FLAG_SIZE + CHUNK_SIZE


def string_to_bytes(msg, num_bytes):
    padded_msg = msg.ljust(num_bytes)
    return padded_msg.encode(encoding="ascii")

def int_to_bytes(number, num_bytes):
    return (number).to_bytes(num_bytes,byteorder="little")


def make_header(host_ip, host_port, flag):
    ip = string_to_bytes(host_ip, IP_SIZE)
    port = int_to_bytes(host_port, PORT_SIZE)
    flag = int_to_bytes(flag, FLAG_SIZE)
    #print("host ip:", ip)
    #print("host port:", int.from_bytes(port, byteorder="little"))
    #print("host flag:", int.from_bytes(flag, byteorder="little"))
    return ip + port + flag


def first_packet_datagram(file_name, host_ip, host_port):
    file_size = os.path.getsize(file_name);
    file_size_bytes = int_to_bytes(file_size, FIRST_SEG_SIZE)
    header = make_header(host_ip, host_port, 1)
    return header + file_size_bytes


def second_packet_datagram(file_name, host_ip, host_port):
    file_name_bytes = string_to_bytes(file_name, SECOND_SEG_SIZE)
    header = make_header(host_ip, host_port, 2)
    return header + file_name_bytes


def generic_packet_datagram(data, host_ip, host_port):
    header = make_header(host_ip, host_port, 3)
    return header + data


def send_packet(s, host, port, data):
    #print("\nSending: ", data)
    s.sendto(data, (host, port))
    return s.recv(DGRAM_SIZE)


############################## Begin script execution ##############################


# Get the input arguments from the commandline call
remote_ip = sys.argv[1]                 # Server IP address
remote_port_number = int(sys.argv[2])   # Server port number
troll_port = int(sys.argv[3])           # Troll port number
file_name = sys.argv[4]                 # Relative path to the file to send


print("Troll port: ", troll_port)
print("Client port: ", CLIENT_PORT)
print("server address: {0}:{1}".format(remote_ip, remote_port_number))

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP uses Datagram, but not stream
s.bind(('', 1567))

datagram = first_packet_datagram(file_name, remote_ip, troll_port)
response = send_packet(s, remote_ip, troll_port, datagram)
time.sleep(0.0015)

datagram = second_packet_datagram(file_name, remote_ip, troll_port)
response = send_packet(s, remote_ip, troll_port, datagram)
time.sleep(0.0015)

chunk_num = 1
with open(file_name, 'rb') as f:
    data = f.read(CHUNK_SIZE)
    while data:
        datagram = generic_packet_datagram(data, remote_ip, remote_port_number)
        response = send_packet(s, remote_ip, troll_port, datagram)
        chunk_num += 1
        data = f.read(CHUNK_SIZE)
        time.sleep(0.0015)
s.close()

print("Finished UPD file transfer")
