CSE 3461: Lab 3
Author: Zach Peugh
Date: 10/10/2016

This lab implements a simple client-server interface
in which a use can spin up a UDP server on a specific port
and then use another machine to send a file through the troll
program to the server where it will be written to disk. It uses
the 'troll' executable as a middleman in order to make sure
that the UPD message gets sent without dropped/rearranged packets.

The server-side file is "ftps.py" and can be run using the command:

    python3 ftps.py <server-port>

where <server-port> is the port you wish to use for the socket.

The file 'troll' must be running also, with the following inputs:

    troll -C <client-host-name> -S <server-host-name> -a 1567
            -b <server-port> -r -s 1 -t -x 0 <troll-port>

<client-host-name>  is the name of the host where the client is running.
<server-host-name>  is the name of the host where the server is running.
1567 is the dedicated client port HARDCODED in.  Just use it.
<server-port> is a port number you can choose
<troll_port> is a port that must be different from 1567


The client-side file is "ftpc.py" and can be run once the server
script has already been launched and is listening.  The command
for transferring a file to the server is

    python3 ftpc.py <server-host-name> <server-port>
                    <troll-port> <relative-file-path>

<server-host-name> is the 4-byte maximum string for the host
(i.e 'beta' or 'sl4', etc).  The program will NOT work given an IP
address/host name over 4-bytes, due to specifications in the lab.
<server-port> is the same one used twice above
<troll-port> is the same port chosen in the troll command
<relative file path> is the name of the file you wish to transfer


*To avoid the issue with host names being too long, (i.e 'localhost',
or '127.0.0.1'), change IP_SIZE=4 to IP_SIZE=8 in ftpc.py and ftps.py.

**There are some commented out print statements that could be helpful
to uncomment for grading the lab.  Idk maybe not.
