CSE 3461: Lab 2

This lab implements a simple client-server interface
in which a use can spin up a server on a specific port
and then use another machine to send a file through a TCP
socket to the server where it will be written to disk.

The server-side file is "ftps.py" and can be run using the command:

    python3 ftps.py <port number>

where <port number> is the port you wish to use for the socket.


The client-side file is "ftpc.py" and can be run once the server
script has already been launched and is listening.  The command
for transferring a file to the server is

    python3 ftpc.py <host name> <port number> <relative file path>

<host name> is the IP address or host name of the machine where the
server script was ran.
<port number> is the port number specified when you ran the server script
<relative file path> is the name of the file you wish to transfer
