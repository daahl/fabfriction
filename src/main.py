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

import matplotlib.pyplot as plt
import numpy as np

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

# Global variables
udp_socket = None
serial_port = None
filename = None

# Parse command line arguments
# https://docs.python.org/3/library/argparse.html
# TODO: add argument for plotting?
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
    global filename

    fileTime = time.localtime()
    filename = 'data_' + str(fileTime.tm_year) + str(fileTime.tm_mon) + str(fileTime.tm_mday) + "_" + str(fileTime.tm_hour) + "-" + str(fileTime.tm_min) + "-" + str(fileTime.tm_sec) + '.csv'

    if(filepath == ''):
        savepath = filename
    else:
        savepath = filepath[0] + "\\" + filename

    with open(savepath, mode='w', newline='') as dataFile:
        dataFile = csv.writer(dataFile, delimiter=';')
        
        dataFile.writerow(['Time', 'vel1', 'vel2', 'Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz'])
        dataFile.writerows(data)

def plot_subplot(time_data, plot_data, xlabel, ax):
    ax.plot(time_data, plot_data[1:])
    ax.set_ylabel(plot_data[0])
    ax.set_xlabel(xlabel)

def plot_data():
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        data = np.array([row for row in csv_reader])

    data = np.transpose(data)   # easier to plot

    fig1, (ax11, ax12) = plt.subplots(2, 1, sharex=True)
    fig2, (ax21, ax22, ax23) = plt.subplots(3, 1, sharex=True)
    fig3, (ax31, ax32, ax33) = plt.subplots(3, 1, sharex=True)

    ax = [ax11, ax12, ax21, ax22, ax23, ax31, ax32, ax33]
    time_data = data[0]
    xlabel = [None, 'Time', None, None, 'Time', None, None, 'Time']

    for i, row in enumerate(data[1:]):
        print(row)
        plot_subplot(time_data[1:], row, xlabel[i], ax[i])

    plt.show()


if __name__ == "__main__":
    data = []

    # Initialize
    num, port = setup_arduino()

    while True:
        if kb.is_pressed('enter'):
            print("Enter pressed. Exiting the loop. Goodbye!")
            break
        
        # Open socket
        # Has to be opened and closed very time to avoid buffering
        setup_netft_udp()
        
        netft_data = read_netft()
        arduino_data = [float(data) for data in read_arduino()]
        time_now = [time.time()]

        close_socket()

        data.append(time_now + arduino_data + netft_data)  # append row

    # Save everything after measuring
    save_to_csv(data)
    close_arduino()

    plot_data()

    
