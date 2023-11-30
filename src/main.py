#
#   Main script for running the friction measurement.
#   FabFriciton group - 2023
#

########## Imports
import keyboard as kb # keyboard interupts during runtime
import time # timestamps and sleep
import argparse as ap # command line argument parser
import csv # save data as csv file
import socket   # for reading force-torque sensor
import struct
import serial   # for reading IR-sensor

# Define constants netft udp
COMMAND_HEADER = 0x1234
RDT_REQUEST_COMMAND = 0x0002  # Replace with the actual command from Table 9.1
SAMPLE_COUNT = 0  # Replace with the desired sample count
UDP_IP = '192.168.125.4'
UDP_PORT = 49152
CPF = 4448221.500
CPT = 112984.8281
LBF2N = 4.44822

BAUDRATE = 115200

udp_socket = None
serial_port = None

# Parse command line arguments
# https://docs.python.org/3/library/argparse.html
cArgsParser = ap.ArgumentParser(description='Process startup arguments.')
cArgsParser.add_argument('-c', '--PORT', action='store', help='Enter port as a string, the format is for Linux: /dev/ttyUSBx. Run this command to check ports: dmesg | grep USB', nargs=1, type=str, default= '/dev/ttyUSB0')
cArgsParser.add_argument('-p', '--PATH', action='store', help='Enter filepath, without trailing "\\", or leave blank to save in same directory.', nargs=1, type=str, default='') 

cArgs = cArgsParser.parse_args()
port = cArgs.PORT
filepath = cArgs.PATH

print('Staring script, press Enter to exit...')
print(f'Given port: {port}')
print(f'Save path: {filepath}')
print('Filename is: data_YYMMDD_HHMMSS.csv')

# Neftft udp
def setup_netft_udp():
    global udp_socket
    # Create a socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Server address and port
    server_address = (UDP_IP, UDP_PORT)  # Replace with the actual server address and port

    #print(f'Sending packet to {UDP_IP} on port {UDP_PORT}...')

    # Create the RDT request structure
    rdt_request = struct.pack('>HHI', COMMAND_HEADER, RDT_REQUEST_COMMAND, SAMPLE_COUNT)

    # Send the RDT request
    udp_socket.sendto(rdt_request, server_address)


def read_netft():
    response, server = udp_socket.recvfrom(36)

    # Unpack the response structure
    rdt_response = struct.unpack('>IIIiiiiii', response)

    # Process the response data
    rdt_sequence, ft_sequence, status, Fx, Fy, Fz, Tx, Ty, Tz = rdt_response

    force = [Fx, Fy, Fz]
    torque = [Tx, Ty, Tz]

    netft_data = [f/CPF * LBF2N for f in force] + [t/CPT * LBF2N for t in torque]

    return netft_data

def close_socket():
    udp_socket.close()


# Serial port
def setup_arduino():
    global serial_port
    try:
        serial_port = serial.Serial(port, BAUDRATE)
        print(serial_port)
        return 1, serial_port
    except Exception as e:
        print("Error opening serial port!")
        print(e)
        return 0
    
def read_arduino():
    global serial_port
    # arduino returns data after incoming "1" on serial
    serial_port.write(1)
    return serial_port.readline().decode('utf-8').strip().split(',')
    
def close_arduino():
    global serial_port
    try:
        serial_port.close()
        return 1
    except Exception as e:
        print("Error closing serial port!")
        print(e)
        return 0
    
def save_to_csv(data):
    # Save data to CSV file
    fileTime = time.localtime()
    filename = 'data_' + str(fileTime.tm_year) + str(fileTime.tm_mon) + str(fileTime.tm_mday) + "_" + str(fileTime.tm_hour) + "-" + str(fileTime.tm_min) + "-" + str(fileTime.tm_sec) + '.csv'

    if(filepath == ''):
        savepath = filename
    else:
        savepath = filepath[0] + "\\" + filename

    with open(savepath, mode='w', newline='') as dataFile:
        dataFile = csv.writer(dataFile, delimiter=';')
        
        dataFile.writerow(['Time', 'Vel', 'Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz'])
        dataFile.writerows(data)

if __name__ == "__main__":
    data = []

    # Initialize
    num, port = setup_arduino()

    while True:
        if kb.is_pressed('enter'):
            print("Enter pressed. Exiting the loop. Goodbye!")
            break
        setup_netft_udp()
        
        arduino_data = [float(data) for data in read_arduino()]
        netft_data = read_netft()
        time_now = [time.time()]

        close_socket()

        data.append(time_now + arduino_data + netft_data)  # append row

    save_to_csv(data)
    close_arduino()

    
