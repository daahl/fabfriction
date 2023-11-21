from pynput import mouse
import time
import math
import tkinter as tk
from termcolor import colored
import matplotlib.pyplot as plt

#Saker som behöver hårdkodas
widht_meter = 345.6/1000
heigth_meter = 194.4/1000
mousepad_width = 0.15
pixels_per_mousepad = 845

root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

pixel_size = widht_meter/screen_width

pixel_per_meter_mousepad = pixels_per_mousepad/mousepad_width
pixels_per_meter_screen = screen_width/widht_meter
#pixel_per_meter_screen = 
ratio_mouse_screen = pixels_per_meter_screen/pixel_per_meter_mousepad

old_speed = 0
old_x, old_y = 0, 0
interval = 0.1  # Set the interval in seconds
x_max = screen_width
x_min = 0
y_max = screen_height
y_min = 0
acceleration_limit = 1
total_duration = 100
timen = 0
time_points = []
speed_points = []

# Create a figure and axis for the plot


def inf_boundaries(current_x, current_y, old_x, old_y):
    distance = 0
    entered_edge = False
    #If we enter edge in x
    if current_x >= x_max or current_x <= x_min:
        #if we enter the right x limit
        if current_x > x_max/2:
            #if we enter the lower right corner
            mouse.Controller().move(-x_max/2, 0)
            new_current_x, new_current_y = mouse.Controller().position
            distance = math.sqrt(((abs(x_max-old_x)+abs(new_current_x-x_max/2)))**2 + (new_current_y-old_y)**2)*pixel_size*ratio_mouse_screen
            current_x = new_current_x
            current_y = new_current_y 

        elif current_x < x_max/2:
            #if we enter the lower left corner
            mouse.Controller().move(x_max/2, 0)
            new_current_x, new_current_y = mouse.Controller().position
            distance = math.sqrt(((abs(x_min-old_x)+abs(new_current_x-x_max/2)))**2 +(new_current_y-old_y)**2)*pixel_size*ratio_mouse_screen
            current_x = new_current_x
            current_y = new_current_y
            

    #if we enter edge in y             
    if current_y >= y_max or current_y <= y_min:
        #if we enter the edge in the bottom
        if current_y > y_max/2:
            mouse.Controller().move(0, -y_max/2)   
            new_current_x, new_current_y = mouse.Controller().position
            distance = math.sqrt((current_x-old_x)**2 + (abs(y_max - old_y) + abs(new_current_y-y_max/2))**2)*pixel_size*ratio_mouse_screen
            current_x = new_current_x
            current_y = new_current_y 
        
        #if we enter the edge in the top
        elif current_y < y_max/2:
            #if we enter the edge in upper right corner
            
            mouse.Controller().move(0, y_max/2)
            new_current_x, new_current_y = mouse.Controller().position
            distance = math.sqrt((current_x-old_x)**2 + (abs(y_min - old_y) + abs(new_current_y-y_max/2))**2)*pixel_size*ratio_mouse_screen
            current_x = new_current_x
            current_y = new_current_y
            
    return distance, current_x, current_y

start_time = time.time()
while True: #time.time() - start_time <= total_duration:

    # Get current mouse position
    current_x, current_y = mouse.Controller().position
    distance, current_x, current_y = inf_boundaries(current_x, current_y, old_x, old_y)
    
    #print(mouse.Controller().position)
    mouse.Controller().position
    # Calculate distance between current and previous position
    if distance == 0:
        distance = math.sqrt((current_x - old_x)**2 + (current_y - old_y)**2)*pixel_size*ratio_mouse_screen
 
    # Calculate speed
    speed = distance / interval
    speed_ratio = abs(speed - old_speed)
    
    timen = timen + interval

    time_points.append(timen)
    speed_points.append(speed)

    if speed > 0: #and speed_ratio < acceleration_limit:
        print(f"Velocity: {speed} meters per second")
    #if speed_ratio >= acceleration_limit:
    #   print(colored("Acceleration limit reached",'red'))

    old_speed = speed
    # Update previous position for the next iteration
    old_x, old_y = current_x, current_y
    #print( mouse.Controller().position)
    # Sleep for the specified interval
    time.sleep(interval)

plt.plot(time_points, speed_points)
plt.xlabel('Time (s)')
plt.ylabel('Speed (m/s)')
plt.title('Mouse Speed Over Time')
plt.show()