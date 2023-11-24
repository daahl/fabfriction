#
#   Script to read/write serial data from/to arduino.
#
import serial
import time

# Constants
PORT = "COM9"
BAUDRATE = 115200

# Open the serial port
ser = serial.Serial(PORT, BAUDRATE)

try:
    # Write data to the serial port
    data_to_send = "2"
    ser.write(data_to_send.encode('utf-8'))  # Encode string to bytes
    print(f"Sent: {data_to_send}")

    time.sleep(1)

    # Read data from the serial port
    received_data = ser.readline().decode('utf-8').strip()
    print(f"Received: {received_data}")

except KeyboardInterrupt:
    print("Execution stopped by user.")

except Exception as e:
    print(f"Error: {e}")

finally:
    ser.close()
