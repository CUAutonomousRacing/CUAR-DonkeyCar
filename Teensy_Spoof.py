from BuffMata import BuffMata
import serial
import math
import time

# Generate mock PWM commands ranging between -1 and 1

# send to buffmata.py
try: 
    test_input = BuffMata(5,6)
    x = 0 # Start at 0
    while True:
        throt_cmd = math.sin(x) # Output should range between -1 and 1
        steer_cmd = math.sin(x) # Output should range between -1 and 1
        print(f"Steering Input: {steer_cmd}, Throttle Input: {throt_cmd}")
        test_input.run(steer_cmd, throt_cmd)
        x += 0.1 # Increment x
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nExiting")
    test_input.shutdown()