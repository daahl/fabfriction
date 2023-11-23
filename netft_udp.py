import socket
import struct

# Define constants
COMMAND_HEADER = 0x1234
RDT_REQUEST_COMMAND = 0x0002  # Replace with the actual command from Table 9.1
SAMPLE_COUNT = 10  # Replace with the desired sample count
UDP_IP = '192.168.125.4'
UDP_PORT = 49152
CPF = 4448221.500
CPT = 112984.8281

# Create a socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server address and port
server_address = (UDP_IP, UDP_PORT)  # Replace with the actual server address and port

print(f'Sending packet to {UDP_IP} on port {UDP_PORT}...')

# Create the RDT request structure
rdt_request = struct.pack('>HHI', COMMAND_HEADER, RDT_REQUEST_COMMAND, SAMPLE_COUNT)

# Send the RDT request
udp_socket.sendto(rdt_request, server_address)

print('Done.')

print('Receiving packets...')

response, server = udp_socket.recvfrom(36)

# Unpack the response structure
rdt_response = struct.unpack('>IIIiiiiii', response)

# Process the response data
rdt_sequence, ft_sequence, status, Fx, Fy, Fz, Tx, Ty, Tz = rdt_response

print(f'Received:\nRDT-seq: {rdt_sequence}\nFT-seq: {ft_sequence}\nStatus: {status}\nFx: {Fx/CPF}\nFy: {Fy/CPF}\nFz: {Fz/CPF}\nTx: {Tx/CPT}\nTy: {Ty/CPT}\nTz: {Tz/CPT}')

# Close the socket
udp_socket.close()