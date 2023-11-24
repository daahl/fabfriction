#
#   Main script for running the friction measurement.
#   FabFriciton group - 2023
#

########## TODO
# Save last used COM port and dest path in config.json and use as default if none is given
# 

########## Imports
import keyboard as kb # keyboard interupts during runtime
import time # timestamps and sleep
import argparse as ap # command line argument parser
import csv # save data as csv file
import socket
import struct

# Define constants netft udp
COMMAND_HEADER = 0x1234
RDT_REQUEST_COMMAND = 0x0002  # Replace with the actual command from Table 9.1
SAMPLE_COUNT = 0  # Replace with the desired sample count
UDP_IP = '192.168.125.4'
UDP_PORT = 49152
CPF = 4448221.500
CPT = 112984.8281
LBF2N = 4.44822

udp_socket = None


def setup_netft_udp():
    global udp_socket
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


def read_netft():
    print('Receiving packets...')

    response, server = udp_socket.recvfrom(36)

    # Unpack the response structure
    rdt_response = struct.unpack('>IIIiiiiii', response)

    # Process the response data
    rdt_sequence, ft_sequence, status, Fx, Fy, Fz, Tx, Ty, Tz = rdt_response

    #print(f'Received:\nRDT-seq: {rdt_sequence}\nFT-seq: {ft_sequence}\nStatus: {status}\nFx: {Fx/CPF}\nFy: {Fy/CPF}\nFz: {Fz/CPF}\nTx: {Tx/CPT}\nTy: {Ty/CPT}\nTz: {Tz/CPT}')
    print(f'Fz: {Fz/CPF * LBF2N}')

    netft_data = [Fx, Fy, Fz, Tx, Ty, Tz]

    return netft_data

def close_socket():
    udp_socket.close()   



if __name__ == "__main__":
    ########## Parse command line arguments
    # https://docs.python.org/3/library/argparse.html
    cArgsParser = ap.ArgumentParser(description='Process startup arguments.')
    cArgsParser.add_argument('-c', '--COM', action='store', help='Enter COM-port number as integer.', nargs=1, required=True, type=int)
    cArgsParser.add_argument('-p', '--PATH', action='store', default='', help='Enter filepath, without trailing "\\", or leave blank to save in same directory.', nargs=1, type=str) 

    cArgs = cArgsParser.parse_args()
    comport = cArgs.COM
    filepath = cArgs.PATH

    ########## Starting data collection
    print('Staring script, press Enter to exit...')
    print(f'Given COM-port: {comport}')
    print(f'Save path: {filepath}')
    print('Filename is: data_YYMMDD_HHMMSS.csv')

    # dummy data
    dumbdata = [[123,100,200,1000],[456,110,210,1100]]

    setup_netft_udp()

    while True:
        if kb.is_pressed('enter'):
            print("Enter pressed. Exiting the loop. Goodbye!")
            break

        netft_data = read_netft()

        print("Press Enter to exit.")
        time.sleep(0.5)  # Optional: Add a small delay to avoid high CPU usage

    close_socket()
    
    ########## Save data to CSV file
    fileTime = time.localtime()
    filename = 'data_' + str(fileTime.tm_year) + str(fileTime.tm_mon) + str(fileTime.tm_mday) + "_" + str(fileTime.tm_hour) + str(fileTime.tm_min) + str(fileTime.tm_sec) + '.csv'

    if(filepath == ''):
        savepath = filename
    else:
        savepath = filepath[0] + "\\" + filename

    with open(savepath, mode='w', newline='') as dataFile:
        dataFile = csv.writer(dataFile, delimiter=';')
        
        dataFile.writerow(['Time', 'Vel1', 'Vel2', 'Force'])
        dataFile.writerows(dumbdata)
