# Custom part to implement Teensy 4.1 microcontroller as an input into the
# controller pipeline. Reads in steering and throttle inputs from Jetson UART
<<<<<<< HEAD
# then translates it into an appropriate PWM signal for digestion into 
# arduino drivetrain.
# Pseudo code example of how the Teensy RC Part will work:
=======
# then translates it into proper channel values for consumption by BuffMata
>>>>>>> 0fbbece198e6f5e7bdf2f4474a45c3c6a0711783
import serial
import time
import threading

<<<<<<< HEAD

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
=======
# NOTE: This is the class template. The format actually used by the program lives in parts/controller.py

class Teensy_RC:
    def __init__(self, serial_device):
        try:
            self.ser = serial_device 
            # self.mode = 'user'
            # self.recording = False
            self.steering = 0.0
            self.throttle = 0.0
            self.running = True
            self.lock = threading.Lock()
            self.thread = threading.Thread(target=self.update, daemon=True) # Start reading from serial
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
    
    def update(self):
        packet_found = False
        buffer = ""
        while self.running:
            try:
                char = self.ser.read().decode('utf-8') # Read from Serial
                print(f"Byte Decoded: {char}")
                if(char == '<'):
                    buffer += "<"
                    packet_found = True
                elif(packet_found):
                    buffer += char
                    if(char == '>'):
                        commands = self.parsePacket(self.buffer) # Read in our packet
                        packet_found = False
                        buffer = ""
                        if commands:
                            print(f"Steering: {commands[0]}, Throttle: {commands[1]}")
                            with self.lock: # For thread safety
                                self.steering = commands[0] # Update steering
                                self.throttle = commands[1] # Update throttle
            except:
                print("No incoming control data detected.")
    
    def run_threaded(self): # Required for threading by vehicle.py
        with self.lock:
            return self.steering, self.throttle
    
    def run(self): # Required by vehicle.py
        return self.run_threaded()
        
    def shutdown(self): # Required for threading by vehicle.py
        self.running = False
        print("Teensy_RC Shutting Down")
>>>>>>> 0fbbece198e6f5e7bdf2f4474a45c3c6a0711783

# update python dictionary channel members /user/steering and /user/throttle with steering and throttle
# so frames are hopefully synced (need to find a way to guarantee this)

<<<<<<< HEAD
# Send steering and throttle commands back to teensy? Or maybe we just use the Teensy program to send those values
# directly to the servos we need. As long as we are syncing those values with the images, we should be ok
=======
>>>>>>> 0fbbece198e6f5e7bdf2f4474a45c3c6a0711783
