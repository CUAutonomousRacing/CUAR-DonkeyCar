# Class to read in values either from a controller (Teensy_RC) or the pilot model to send PWM commands to 
# the control Teensy
import serial
import time

class BuffMata:
    def __init__(self, STEERING_PIN, THROTTLE_PIN, port = '/dev/ttyTHS1', baud=115200, bytesize = 8):
        try:
            self.ser = serial.Serial(port,baud,bytesize) # Open UART RX serial port
            time.sleep(0.05)
            print(f"{self.ser.name} opened successfully!") # Print name of serial port to console once opened
            self.steeringPin = STEERING_PIN
            self.throttlePin = THROTTLE_PIN
            self.running = True
            print("BuffMata created")
        except serial.SerialException as e:
            print(f"Failed to open: {e}")
            print("Exiting")
            exit()
    
    def mapSteerPWM(self, steering):
        return 90 + steering*45 # Full Left = 45 (-1); Full Right = 135 (1); Center = 90 (0)
    
    def mapThrottlePWM(self, throttle):
        return 90 + throttle*30 # Full Throttle = 120 (1); Full Reverse = 70 (-1); Deadzone = 90-98 (0-ish)
    
    def checkSum(self, packet): # Simple XOR Checksum, might not be sufficient 
        cs = 0
        for byte in packet.encode():
            cs ^= byte
        return cs
    
    def run(self, steering, throttle):
        steering = self.mapSteerPWM(max(-1.0, min(1.0, steering))) # Clamping
        throttle = self.mapThrottlePWM(max(-1.0, min(1.0, throttle))) # Clamping
        cmd = f"{self.steeringPin},{int(steering)},{self.throttlePin},{int(throttle)}"
        cs = self.checkSum(cmd) # Checksum for packet loss validation
        packet = f"<{cmd}|{cs}>\n" 
        # '<' packet start; {steerpin,steerPWM,throttlepin,throttlePWM}; '|' Cmd/cs Delimiter; '>' packet end; '\n' for marking end of line
        self.ser.write(packet.encode())

    def shutdown(self):
        # set steering straight
        cmd = f"{self.steeringPin} {90}\n" # Sends steering command as PWM between 0-255
        self.ser.write(cmd.encode())
        cmd = f"{self.throttlePin} {90}\n" # Sends throttle command as PWM between 0-255
        self.ser.write(cmd.encode())
        time.sleep(0.3)
        self.running = False
        self.ser.close()
        print("BuffMata Shutting Down")
