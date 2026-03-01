# Custom part to implement Teensy 4.1 microcontroller as an input into the
# controller pipeline. Reads in steering and throttle inputs from Jetson UART
# then translates it into an appropriate PWM signal for digestion into 
# arduino drivetrain.
# Pseudo code example of how the Teensy RC Part will work:
import serial
import time
import threading


class Teensy_RC:
    def __init__(self, port = '/dev/ttyTHS1', baud=115200, timeout=1):
        try:
            self.ser = serial.Serial(port,baud,timeout) # Open UART RX serial port
            print(f"{self.ser.name} opened successfully!") # Print name of serial port to console once opened
            self.angle = 0.0
            self.throttle = 0.0
            self.running = True
            self.lock = threading.Lock()
        except serial.SerialException as e:
            print(f"Failed to open: {e}")
            print("Exiting")
            exit()

    def run_threaded(self):
        incomingData = self.ser.readline().decode('utf-8').strip()
        while incomingData:
            commands = incomingData.split(',')
            steering = commands[0] # Angle will be sent first, already turned into a +/- 1 value by the teensy for PWM
            throttle = commands[1] # Throttle sent next, already turned into a +/- 1 value by the teensy for PWM
        return steering, throttle
    
    def run(self):
        self.run_threaded()
    def shutdown(self):
        self.running = False
        print("Teensy_RC Shutting Down")
        self.ser.close() # Close the serial port

# update python dictionary channel members /user/steering and /user/throttle with steering and throttle
# so frames are hopefully synced (need to find a way to guarantee this)

# Send steering and throttle commands back to teensy? Or maybe we just use the Teensy program to send those values
# directly to the servos we need. As long as we are syncing those values with the images, we should be ok
