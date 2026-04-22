import os

# Set the pin factory to pigpio for hardware PWM before importing gpiozero
os.environ['GPIOZERO_PIN_FACTORY'] = 'pigpio'

from gpiozero import Servo
from time import sleep

# MS24 Pulse Widths: 0.5ms to 2.5ms
# On Pi 4, GPIO 18 is Physical Pin 12
motor = Servo(18, min_pulse_width=0.0005, max_pulse_width=0.0025)

print("Pi 4B + MS24 Test Starting...")

def activate_four_wheel(four_engaged):
    if not four_engaged:
        motor.value = 0.5
    return four_engaged

def deactive_four_wheel(four_engaged):
    if four_engaged:
        motor.value = -0.5
    return four_engaged