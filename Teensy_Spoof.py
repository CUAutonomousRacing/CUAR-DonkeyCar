import serial
import time
import math

ser = serial.Serial(
    port='/dev/ttyTHS1',
    baudrate=115200,
    timeout=1
)

print("Spoofing RC commands...")

t = 0.0
while True:
    angle = 0.5 * math.sin(t)
    throttle = 0.3 * math.cos(t)

    msg = f"{angle:.3f},{throttle:.3f}\n"
    ser.write(msg.encode('utf-8'))

    print("Sent:", msg.strip())

    t += 0.1
    time.sleep(0.05)