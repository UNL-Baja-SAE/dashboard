from gpiozero import Servo
from time import sleep

# MS24 Pulse Widths: 0.5ms to 2.5ms
# On Pi 4, GPIO 18 is Physical Pin 12
motor = Servo(18, min_pulse_width=0.0005, max_pulse_width=0.0025)

print("Pi 4B + MS24 Test Starting...")

def activate_four_wheel(four_engaged):
    if not four_engaged:
        print("eaaengaged")
        motor.value = 0.5
        four_engaged = True
    return four_engaged

def deactive_four_wheel(four_engaged):
    if four_engaged:
        print("disaaengaged")
        motor.value = -0.5
        four_engaged = False
    return four_engaged