# import serial
# import time

# ser = serial.Serial('/dev/ttyTHS1', baudrate=57600)

# time.sleep(2)

# ser.write(b'A')
# print("Sent:A")

# received = ser.read()
# print(f"Received: {received}")

# ser.close()
# """
# Test UART communication between Jetson Nano and Teensy (Firmata on Serial2)
# Requires pymata-aio:
#     pip install pymata-aio
# """

# import asyncio
# from pymata_aio.pymata3 import PyMata3
# import time

# # Adjust for your Jetson UART port and baud
# PORT = "/dev/ttyTHS1"
# BAUD = 57600

# # Teensy pins to test
# LED_PIN = 13         # Onboard LED or digital output
# PWM_PIN = 14         # PWM-capable pin for servo/ESC
# BUTTON_PIN = 11      # Optional input for testing

# async def main():
#     print(f"Connecting to Teensy on {PORT} at {BAUD} baud...")
#     board = PyMata3(com_port=PORT)
#     print("Connected!")

#     # --- Test 1: Digital Output (LED blink) ---
#     print("\n[TEST 1] Blinking LED on pin", LED_PIN)
#     board.set_pin_mode_digital_output(LED_PIN)

#     for i in range(5):
#         board.digital_write(LED_PIN, 1)
#         print("LED ON")
#         await asyncio.sleep(0.5)
#         board.digital_write(LED_PIN, 0)
#         print("LED OFF")
#         await asyncio.sleep(0.5)

#     # --- Test 2: PWM Output ---
#     print("\n[TEST 2] PWM sweep on pin", PWM_PIN)
#     board.set_pin_mode_pwm_output(PWM_PIN)

#     for val in range(0, 256, 25):
#         board.analog_write(PWM_PIN, val)
#         print(f"PWM value: {val}")
#         await asyncio.sleep(0.3)

#     board.analog_write(PWM_PIN, 0)
#     print("PWM test complete.")

#     # --- Test 3: Digital Input (optional button) ---
#     print("\n[TEST 3] Reading digital input on pin", BUTTON_PIN)
#     board.set_pin_mode_digital_input(BUTTON_PIN)

#     for _ in range(10):
#         val = board.digital_read(BUTTON_PIN)
#         print(f"Button value: {val}")
#         await asyncio.sleep(0.5)

#     print("\nAll tests complete.")
#     board.shutdown()

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     try:
#         loop.run_until_complete(main())
#     finally:
#         loop.close()

    # asyncio.run(main())
# from pymata_aio.pymata3 import PyMata3
# import asyncio

# async def main():
#     board = PyMata3(com_port="/dev/ttyTHS1", baud_rate=57600)
#     await asyncio.sleep(2)
#     print("Connected to board")

#     await board.set_pin_mode_digital_output(13)
#     for _ in range(5):
#         await board.digital_write(13,1)
#         await asyncio.sleep(0.5)
#         await board.digital_write(13,0)
#         await asyncio.sleep(0.5)

#     await board.shutdown()

# asyncio.run(main())
from PyMata.pymata import PyMata
import time

board = PyMata("/dev/ttyTHS1", 57600)

time.sleep(2)
print("Connected!")

board.set_pin_mode(13, board.OUTPUT)

for i in range(5):
    board.digital_write(13, 1)
    time.sleep(0.5)
    board.digital_write(13, 0)
    time.sleep(0.5)

board.close()

