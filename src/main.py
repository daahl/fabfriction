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

while True:
    if kb.is_pressed('enter'):
        print("Enter pressed. Exiting the loop. Goodbye!")
        break

    print("Press Enter to exit.")
    time.sleep(0.5)  # Optional: Add a small delay to avoid high CPU usage

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

    
