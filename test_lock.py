import os
os.environ['GPIOZERO_PIN_FACTORY'] = 'pigpio'
from gpiozero import Servo
from time import sleep

# Initialize the servo. This instantly commands it to center (0.0)
motor = Servo(18, min_pulse_width=0.0005, max_pulse_width=0.0025)

print("Signal sent. The motor should be locked right now.")
print("Try to spin the motor horn with your fingers.")

# Keep the script alive for 10 seconds to maintain the lock
sleep(100)
print("Test over. Motor will unlock.")