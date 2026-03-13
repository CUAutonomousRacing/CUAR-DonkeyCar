# Custom part to implement Teensy 4.1 microcontroller as an input into the
# controller pipeline. Reads in steering and throttle inputs from Jetson UART
# then translates it into proper channel values for consumption by BuffMata
import serial
import time
import threading

# NOTE: This is the class template. The format actually used by the program lives in parts/controller.py

class Teensy_RC:
    def __init__(self, serial_device):
        try:
            self.ser = serial_device 
            self.mode = 'user'
            self.recording = False
            self.steering = 0.0
            self.throttle = 0.0
            self.running = True
            self.lock = threading.Lock()
            self.thread = threading.Thread(target=self.read_serial, daemon=True) # Start reading from serial
            self.thread.start() # Start thread
            print("Teensy RC thread created successfully!")
        except:
            print("Failed to create Teensy RC")
            exit()
    
    def verifyCheckSum(self, parsed_packet, received_check_sum):
        check_sum = 0
        for c in parsed_packet:
            check_sum ^= ord(c)
        return int(received_check_sum) == check_sum
    
    def parsePacket(self, incomingData):
        full_packet_detected = False
        packet_start_found = False
        for c in incomingData: # Find frame delimiters to verify we actually received a full packet
            if(c == '<'):
                packet_start_found = True
            if(packet_start_found and c == '>'):
                full_packet_detected = True
                incomingData = incomingData[1:-1] # Strip our frame delimiters
                parsed_packet = incomingData.split('|') # Split into command data and checksum
                break
        if(full_packet_detected and self.verifyCheckSum(parsed_packet[0], parsed_packet[1])):
            commands = parsed_packet[0].split(',') # Split into Steering and Throttle values
            steering = commands[0] # Steering will be sent first, already turned into a +/- 1 value by the teensy for PWM
            throttle = commands[1] # Throttle sent next, already turned into a +/- 1 value by the teensy for PWM
            return float(steering), float(throttle)
        else:
            print("Full Teensy RC packet not detected. Returning.")
            return None
    
    def read_serial(self):
        while self.running:
            try:
                incomingData = self.ser.readline().decode('utf-8').strip() # Read from UART
                commands = self.parsePacket(incomingData) # Read in our packet
                if commands: # Only updates if commands are available
                    with self.lock: # For thread safety
                        self.steering = commands[0] # Update steering
                        self.throttle = commands[1] # Update throttle
            except:
                print("No incoming control data detected.")
    
    def run_threaded(self, mode, recording): # Required for threading by vehicle.py
        with self.lock:
            return self.steering, self.throttle, self.mode, self.recording
    
    def run(self, mode, recording): # Required by vehicle.py
        return self.run_threaded(mode, recording)
        
    def shutdown(self): # Required for threading by vehicle.py
        self.running = False
        print("Teensy_RC Shutting Down")

# update python dictionary channel members /user/steering and /user/throttle with steering and throttle
# so frames are hopefully synced (need to find a way to guarantee this)

