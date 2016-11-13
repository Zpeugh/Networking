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
IP_SIZE = 10             # The size in bytes of the IP server host name
PORT_SIZE = 2           # The size in bytes of the server port number
FLAG_SIZE = 1           # The size in bytes of the flag
SEQ_NUM_SIZE = 1        # The size in bytes of the sequence number
CHUNK_SIZE = 1000       # The size in bytes of chunks of file to receive at a time
CLIENT_PORT = 1567      # Arbitrarily chosen client port number to bind to
TIMEOUT = 0.05
SERVER_RESP_SIZE = CHUNK_SIZE
DGRAM_SIZE = IP_SIZE + PORT_SIZE + FLAG_SIZE + SEQ_NUM_SIZE + CHUNK_SIZE


def string_to_bytes(msg, num_bytes):
    padded_msg = msg.ljust(num_bytes)
    return padded_msg.encode(encoding="ascii")

def int_to_bytes(number, num_bytes):
    return (number).to_bytes(num_bytes,byteorder="little")


def make_header(host_ip, host_port, flag, seq_bit):
    ip = string_to_bytes(host_ip, IP_SIZE)
    port = int_to_bytes(host_port, PORT_SIZE)
    flag = int_to_bytes(flag, FLAG_SIZE)
    seq_bit = int_to_bytes(seq_bit, SEQ_NUM_SIZE)
    #print("host ip:", ip)
    #print("host port:", int.from_bytes(port, byteorder="little"))
    #print("host flag:", int.from_bytes(flag, byteorder="little"))
    return ip + port + flag + seq_bit


def first_packet_datagram(file_name, host_ip, host_port):
    file_size = os.path.getsize(file_name);
    file_size_bytes = int_to_bytes(file_size, FIRST_SEG_SIZE)
    header = make_header(host_ip, host_port, 1, 0)
    return header + file_size_bytes


def second_packet_datagram(file_name, host_ip, host_port):
    file_name_bytes = string_to_bytes(file_name, SECOND_SEG_SIZE)
    header = make_header(host_ip, host_port, 2, 1)
    return header + file_name_bytes

def final_packet_datagram(host_ip, host_port, seq_bit):
    header = make_header(host_ip, host_port, 4, seq_bit)
    return header

def create_packet_datagram(data, host_ip, host_port, seq_bit):
    header = make_header(host_ip, host_port, 3, seq_bit)
    return header + data


def send_packet(s, host, port, data):
    #print("\nSending: ", data)
    s.sendto(data, (host, port))
    return s.recv(DGRAM_SIZE)

def ack_not_recieved(ack, expected_seq_bit):
    print("ack: {0}".format(ack))
    print("expected ACK: {0}".format(expected_seq_bit))
    if ack is None:
        return True
    else:
        expected_bytes = (expected_seq_bit).to_bytes(SEQ_NUM_SIZE,byteorder="little")
        print("ACK valid: {0}".format(ack == expected_bytes))
        return ack != expected_bytes


# return the compliment seq_bitber after successfully sending
# datagram and recieving an ACK
def send_until_ack(s, datagram, seq_bit, remote_ip, remote_port):
    t_0 = time.time()
    t_elapsed = 0
    unsucessful = True
    response = None
    while unsucessful:
        while (ack_not_recieved(response, seq_bit) and t_elapsed < TIMEOUT):
            response = send_packet(s, remote_ip, remote_port, datagram)
            t_elapsed = time.time() - t_0
        if t_elapsed >= TIMEOUT:
            print("time elapsed")
            t_0 = time.time()
            t_elapsed = 0
        else:
            unsucessful = False
    return int(seq_bit == False)

############################## Begin script execution ##############################


# Get the input arguments from the commandline call
remote_ip = sys.argv[1]                 # Server IP address
remote_port_number = int(sys.argv[2])   # Server port number
troll_port = int(sys.argv[3])           # Troll port number
file_name = sys.argv[4]                 # Relative path to the file to send
seq_bit = 0

print("Troll port: ", troll_port)
print("Client port: ", CLIENT_PORT)
print("server address: {0}:{1}".format(remote_ip, remote_port_number))

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP uses Datagram, but not stream
s.bind(('', 1567))


datagram = first_packet_datagram(file_name, remote_ip, troll_port)
seq_bit = send_until_ack(s, datagram, seq_bit, remote_ip, troll_port)
time.sleep(0.0015)
print("made it 1, seq bit = {0}".format(seq_bit))

datagram = second_packet_datagram(file_name, remote_ip, troll_port)
seq_bit = send_until_ack(s, datagram, seq_bit, remote_ip, troll_port)
time.sleep(0.0015)
print("made it 2, seq bit = {0}".format(seq_bit))

with open(file_name, 'rb') as f:
    data = f.read(CHUNK_SIZE)
    while data:
        datagram = create_packet_datagram(data, remote_ip, remote_port_number, seq_bit)
        seq_bit = send_until_ack(s, datagram, seq_bit, remote_ip, troll_port)
        data = f.read(CHUNK_SIZE)
    datagram = final_packet_datagram(remote_ip, remote_port_number, seq_bit)
    send_until_ack(s, datagram, seq_bit, remote_ip, troll_port)
s.close()

print("Finished UPD file transfer")
