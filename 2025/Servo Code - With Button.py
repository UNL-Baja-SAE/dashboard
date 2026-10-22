from machine import Pin,PWM
import time

MIN = 500000
MAX = 1000000

button = Pin(16,Pin.IN,Pin.PULL_UP)
pwm = PWM(Pin(15))
pwm.freq(50)
x = 1
while True:
    if button.value() == 1:
        time.sleep(0.01)
    else:
        if x == 1:
            pwm.duty_ns(MAX)
            print("Engaged")
            if x == 1:
                x = 1-x
            elif x == 0:
                x =1-x
        elif x == 0:
            pwm.duty_ns(MIN)
            print("Disengaged")
            if x == 1:
                x = 1-x
            elif x == 0:
                x =1-x 
    time.sleep(2)

        
